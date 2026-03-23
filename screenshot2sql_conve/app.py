"""
Streamlit web application for Screenshot2SQL.
"""

import os

import streamlit as st

from .analyzer import ScreenshotAnalyzer
from .schema import SchemaGenerator
from .exporter import MermaidExporter, SQLAlchemyExporter
from .differ import SchemaDiffer


# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Screenshot2SQL",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Analysis helpers (defined before use) ────────────────────────────────────

def run_analysis(
    image_bytes=None,
    image_path=None,
    hint=None,
    force_mock=False,
    api_key="",
    mock_mode=True,
):
    """Run analysis and render results in tabs."""
    analyzer = ScreenshotAnalyzer(
        api_key=api_key if not force_mock else "",
        mock_mode=force_mock or mock_mode,
    )
    generator = SchemaGenerator()
    mermaid_exp = MermaidExporter()
    sqlalchemy_exp = SQLAlchemyExporter()

    with st.spinner("Analyzing UI structure..."):
        analysis = analyzer.analyze(
            image_path=image_path,
            image_bytes=image_bytes,
            hint=hint,
        )

    if not analysis.get("is_ui", False):
        st.error(
            f"❌ {analysis.get('error', 'No UI detected.')}\n\n"
            "This image doesn't appear to be a software UI screenshot."
        )
        return

    stats = generator.get_stats(analysis)
    is_mock = stats["is_mock"]

    col_h1, col_h2, col_h3, col_h4 = st.columns([3, 1, 1, 1])
    with col_h1:
        st.subheader(f"✅ Detected: **{stats['ui_type']}**")
        st.caption(analysis.get("description", ""))
        if stats.get("analyzed_at"):
            st.caption(f"Analyzed: {stats['analyzed_at']}")
    with col_h2:
        st.metric("Confidence", f"{stats['confidence']:.0%}")
        if is_mock:
            st.caption("🎭 Demo mode")
    with col_h3:
        st.metric("Tables", stats["table_count"])
    with col_h4:
        st.metric("Columns", stats["total_columns"])

    st.divider()

    try:
        schema_ddl = generator.generate_schema(analysis)
        sample_queries = generator.generate_sample_queries(analysis)
        full_output = generator.format_full_output(analysis)
        json_output = generator.format_json_output(analysis)
        mermaid_output = mermaid_exp.generate(analysis)
        sqlalchemy_output = sqlalchemy_exp.generate(analysis)
        is_valid, error = generator.validate_schema(schema_ddl)
    except ValueError as exc:
        st.error(f"Schema generation failed: {exc}")
        return

    ui_slug = stats["ui_type"].lower().replace(" ", "_").replace("/", "_")

    tab_schema, tab_queries, tab_mermaid, tab_orm, tab_full, tab_json, tab_entities = st.tabs(
        ["📋 Schema DDL", "🔍 Queries", "📊 ER Diagram", "🐍 SQLAlchemy", "📄 Full SQL", "🔧 JSON", "🗂️ Entities"]
    )

    with tab_schema:
        st.caption(f"{'✅ Valid SQLite schema' if is_valid else f'⚠️ Validation warning: {error}'}")
        st.caption(
            f"{stats['table_count']} tables · {stats['total_columns']} columns · "
            f"{stats['fk_count']} foreign keys"
        )
        st.code(schema_ddl, language="sql")
        st.download_button(
            "⬇️ Download schema.sql",
            schema_ddl,
            file_name=f"{ui_slug}_schema.sql",
            mime="text/plain",
        )

    with tab_queries:
        if not sample_queries:
            st.info("No sample queries generated.")
        for i, q in enumerate(sample_queries, 1):
            st.markdown(f"**{i}. {q.get('description', 'Query')}**")
            st.code(q.get("sql", ""), language="sql")

    with tab_mermaid:
        st.markdown(
            "Copy into [mermaid.live](https://mermaid.live) or any Mermaid-compatible "
            "renderer to visualize the ER diagram."
        )
        st.code(mermaid_output, language="text")
        st.download_button(
            "⬇️ Download diagram.mmd",
            mermaid_output,
            file_name=f"{ui_slug}.mmd",
            mime="text/plain",
        )

    with tab_orm:
        st.markdown("SQLAlchemy 2.x ORM models, ready to drop into your Python project.")
        st.code(sqlalchemy_output, language="python")
        st.download_button(
            "⬇️ Download models.py",
            sqlalchemy_output,
            file_name=f"{ui_slug}_models.py",
            mime="text/plain",
        )

    with tab_full:
        st.code(full_output, language="sql")
        st.download_button(
            "⬇️ Download full output",
            full_output,
            file_name=f"{ui_slug}_full.sql",
            mime="text/plain",
        )

    with tab_json:
        st.markdown("Raw analysis result including metadata and stats.")
        st.code(json_output, language="json")
        st.download_button(
            "⬇️ Download analysis.json",
            json_output,
            file_name=f"{ui_slug}_analysis.json",
            mime="application/json",
        )

    with tab_entities:
        entities = analysis.get("entities", [])
        for entity in entities:
            with st.expander(
                f"📦 **{entity['name']}** — {entity.get('description', '')} "
                f"({len(entity.get('fields', []))} columns)"
            ):
                fields = entity.get("fields", [])
                if fields:
                    data = {
                        "Column": [f["name"] for f in fields],
                        "Type": [f["type"] for f in fields],
                        "Constraints": [f.get("constraints", "") for f in fields],
                    }
                    st.table(data)


def run_compare(hint_a, hint_b, bytes_a, bytes_b, api_key, mock_mode):
    """Run two analyses and show a schema diff."""
    analyzer = ScreenshotAnalyzer(api_key=api_key, mock_mode=mock_mode)
    generator = SchemaGenerator()
    differ = SchemaDiffer()

    with st.spinner("Analyzing both screenshots..."):
        kw_a = {"image_bytes": bytes_a, "hint": hint_a} if bytes_a else {"hint": hint_a}
        kw_b = {"image_bytes": bytes_b, "hint": hint_b} if bytes_b else {"hint": hint_b}
        analysis_a = analyzer.analyze(**kw_a)
        analysis_b = analyzer.analyze(**kw_b)

    if not analysis_a.get("is_ui") or not analysis_b.get("is_ui"):
        st.error("Both screenshots must show a UI to compare schemas.")
        return

    diff = differ.compare(analysis_a, analysis_b)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"A: {analysis_a.get('ui_type')}")
        stats_a = generator.get_stats(analysis_a)
        st.caption(f"{stats_a['table_count']} tables · {stats_a['total_columns']} columns")
    with col2:
        st.subheader(f"B: {analysis_b.get('ui_type')}")
        stats_b = generator.get_stats(analysis_b)
        st.caption(f"{stats_b['table_count']} tables · {stats_b['total_columns']} columns")

    st.divider()

    if not diff.has_changes:
        st.success("✅ No structural differences detected between the two schemas.")
    else:
        col_add, col_rem, col_mod = st.columns(3)
        with col_add:
            st.metric("Tables Added", len(diff.added_tables))
        with col_rem:
            st.metric("Tables Removed", len(diff.removed_tables))
        with col_mod:
            st.metric("Tables Modified", len(diff.modified_tables))

    tab_diff_md, tab_diff_summary = st.tabs(["📄 Diff Report", "📝 Summary"])

    with tab_diff_md:
        report = diff.to_markdown()
        st.markdown(report)
        st.download_button(
            "⬇️ Download diff report",
            report,
            file_name="schema_diff.md",
            mime="text/plain",
        )

    with tab_diff_summary:
        st.text(diff.summary())


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🗄️ Screenshot2SQL")
    st.caption("Reverse-engineer any SaaS UI into a SQL schema")
    st.divider()

    api_key = st.text_input(
        "Anthropic API Key",
        value=os.getenv("ANTHROPIC_API_KEY", ""),
        type="password",
        help="Leave blank to use demo mode with pre-built schemas",
    )

    mock_mode = not bool(api_key)
    if mock_mode:
        st.info(
            "🎭 **Demo mode** — using pre-built schemas.\nAdd your API key for real analysis.",
            icon="ℹ️",
        )
    else:
        st.success("✅ API key set — using Claude vision", icon="✅")

    st.divider()
    st.markdown("**Try these demo UIs:**")
    st.markdown("- 🛍️ Shopify → ecommerce schema")
    st.markdown("- 🐦 Twitter/X → social graph")
    st.markdown("- 📝 Notion → content management")
    st.markdown("- 🐙 GitHub → repos & PRs")
    st.markdown("- 💬 Slack → messaging workspace")
    st.markdown("- 💳 Stripe → payments & billing")
    st.markdown("- 📋 Linear → issue tracking")
    st.divider()
    st.caption("Built autonomously using [NEO](https://heyneo.so)")


# ── Main layout ───────────────────────────────────────────────────────────────
st.markdown("## 📸 → 🗄️  Screenshot to SQL Schema")
st.markdown(
    "Drop any SaaS UI screenshot and get an instant SQL schema, ER diagram, "
    "SQLAlchemy models, and sample queries. "
    "Perfect for product managers, engineers, and founders."
)

mode = st.radio(
    "Mode",
    ["Single Screenshot", "Compare Two Screenshots"],
    horizontal=True,
    label_visibility="collapsed",
)

if mode == "Single Screenshot":
    uploaded_file = st.file_uploader(
        "Drag & drop a UI screenshot",
        type=["png", "jpg", "jpeg", "webp"],
        help="Upload a screenshot of any web or mobile application",
    )

    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    demo_choice = None
    with col1:
        if st.button("🛍️ Shopify", use_container_width=True):
            demo_choice = "shopify"
    with col2:
        if st.button("🐦 Twitter", use_container_width=True):
            demo_choice = "twitter"
    with col3:
        if st.button("📝 Notion", use_container_width=True):
            demo_choice = "notion"
    with col4:
        if st.button("🐙 GitHub", use_container_width=True):
            demo_choice = "github"
    with col5:
        if st.button("💬 Slack", use_container_width=True):
            demo_choice = "slack"
    with col6:
        if st.button("💳 Stripe", use_container_width=True):
            demo_choice = "stripe"
    with col7:
        if st.button("📋 Linear", use_container_width=True):
            demo_choice = "linear"

    st.divider()

    if uploaded_file is not None:
        col_img, col_result = st.columns([1, 2])
        with col_img:
            st.image(uploaded_file, caption="Uploaded screenshot", use_container_width=True)
        with col_result:
            run_analysis(
                image_bytes=uploaded_file.getvalue(),
                hint=uploaded_file.name,
                api_key=api_key,
                mock_mode=mock_mode,
            )
    elif demo_choice is not None:
        st.info(f"Running demo analysis for **{demo_choice.title()}**...")
        run_analysis(hint=demo_choice, force_mock=True, api_key=api_key, mock_mode=mock_mode)
    else:
        st.markdown(
            """
            <div style='text-align:center; padding: 3rem 1rem; color: #888;'>
                <h2>⬆️ Upload a screenshot to get started</h2>
                <p>Or click one of the demo buttons above to see an example.</p>
                <br/>
                <p>Supports: Shopify, Twitter, Notion, GitHub, Slack, Stripe, Linear, and many more</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

else:  # Compare mode
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Screenshot A (before)**")
        file_a = st.file_uploader(
            "Upload screenshot A", type=["png", "jpg", "jpeg", "webp"], key="file_a"
        )
        demo_a = st.selectbox(
            "Or pick a demo (A)",
            ["", "shopify", "twitter", "notion", "github", "slack", "stripe", "linear"],
            key="demo_a",
        )
    with col_b:
        st.markdown("**Screenshot B (after)**")
        file_b = st.file_uploader(
            "Upload screenshot B", type=["png", "jpg", "jpeg", "webp"], key="file_b"
        )
        demo_b = st.selectbox(
            "Or pick a demo (B)",
            ["", "shopify", "twitter", "notion", "github", "slack", "stripe", "linear"],
            key="demo_b",
        )

    st.divider()

    hint_a = file_a.name if file_a else demo_a
    hint_b = file_b.name if file_b else demo_b

    if hint_a and hint_b:
        run_compare(
            hint_a=hint_a,
            hint_b=hint_b,
            bytes_a=file_a.getvalue() if file_a else None,
            bytes_b=file_b.getvalue() if file_b else None,
            api_key=api_key,
            mock_mode=mock_mode,
        )
    else:
        st.info("Select or upload two screenshots to compare their schemas.")
