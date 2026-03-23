"""Mock responses for demo/test mode when no API key is set."""

MOCK_RESPONSES = {
    "shopify": {
        "is_ui": True,
        "ui_type": "Shopify Admin",
        "confidence": 0.97,
        "description": "Shopify admin dashboard showing product management, order tracking, and customer data.",
        "entities": [
            {
                "name": "products",
                "description": "Product catalog with variants and inventory",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "title", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "description", "type": "TEXT", "constraints": ""},
                    {"name": "vendor", "type": "VARCHAR(255)", "constraints": ""},
                    {"name": "product_type", "type": "VARCHAR(100)", "constraints": ""},
                    {"name": "handle", "type": "VARCHAR(255)", "constraints": "UNIQUE NOT NULL"},
                    {"name": "status", "type": "VARCHAR(20)", "constraints": "DEFAULT 'active'"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                    {"name": "updated_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "product_variants",
                "description": "Product variants with pricing and inventory",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "product_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES products(id)"},
                    {"name": "title", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "sku", "type": "VARCHAR(100)", "constraints": "UNIQUE"},
                    {"name": "price", "type": "DECIMAL(10,2)", "constraints": "NOT NULL"},
                    {"name": "compare_at_price", "type": "DECIMAL(10,2)", "constraints": ""},
                    {"name": "inventory_quantity", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "weight", "type": "DECIMAL(8,2)", "constraints": ""},
                    {"name": "option1", "type": "VARCHAR(255)", "constraints": ""},
                    {"name": "option2", "type": "VARCHAR(255)", "constraints": ""},
                    {"name": "barcode", "type": "VARCHAR(100)", "constraints": ""},
                ],
            },
            {
                "name": "customers",
                "description": "Customer accounts and contact information",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "email", "type": "VARCHAR(255)", "constraints": "UNIQUE NOT NULL"},
                    {"name": "first_name", "type": "VARCHAR(100)", "constraints": ""},
                    {"name": "last_name", "type": "VARCHAR(100)", "constraints": ""},
                    {"name": "phone", "type": "VARCHAR(20)", "constraints": ""},
                    {"name": "accepts_marketing", "type": "BOOLEAN", "constraints": "DEFAULT FALSE"},
                    {"name": "total_spent", "type": "DECIMAL(10,2)", "constraints": "DEFAULT 0"},
                    {"name": "orders_count", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "tags", "type": "TEXT", "constraints": ""},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "orders",
                "description": "Customer orders with line items and fulfillment status",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "order_number", "type": "INTEGER", "constraints": "UNIQUE NOT NULL"},
                    {"name": "customer_id", "type": "INTEGER", "constraints": "REFERENCES customers(id)"},
                    {"name": "email", "type": "VARCHAR(255)", "constraints": ""},
                    {"name": "financial_status", "type": "VARCHAR(50)", "constraints": ""},
                    {"name": "fulfillment_status", "type": "VARCHAR(50)", "constraints": ""},
                    {"name": "total_price", "type": "DECIMAL(10,2)", "constraints": "NOT NULL"},
                    {"name": "subtotal_price", "type": "DECIMAL(10,2)", "constraints": ""},
                    {"name": "total_tax", "type": "DECIMAL(10,2)", "constraints": "DEFAULT 0"},
                    {"name": "currency", "type": "VARCHAR(3)", "constraints": "DEFAULT 'USD'"},
                    {"name": "note", "type": "TEXT", "constraints": ""},
                    {"name": "tags", "type": "TEXT", "constraints": ""},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "order_line_items",
                "description": "Individual products within an order",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "order_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES orders(id)"},
                    {"name": "variant_id", "type": "INTEGER", "constraints": "REFERENCES product_variants(id)"},
                    {"name": "title", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "quantity", "type": "INTEGER", "constraints": "NOT NULL DEFAULT 1"},
                    {"name": "price", "type": "DECIMAL(10,2)", "constraints": "NOT NULL"},
                    {"name": "sku", "type": "VARCHAR(100)", "constraints": ""},
                    {"name": "vendor", "type": "VARCHAR(255)", "constraints": ""},
                ],
            },
        ],
        "sample_queries": [
            {
                "description": "Top selling products by revenue",
                "sql": """SELECT
    p.title,
    SUM(oli.quantity) AS units_sold,
    SUM(oli.quantity * oli.price) AS revenue
FROM products p
JOIN product_variants pv ON pv.product_id = p.id
JOIN order_line_items oli ON oli.variant_id = pv.id
JOIN orders o ON o.id = oli.order_id
WHERE o.financial_status = 'paid'
GROUP BY p.id, p.title
ORDER BY revenue DESC
LIMIT 10;""",
            },
            {
                "description": "Customer lifetime value",
                "sql": """SELECT
    c.email,
    c.first_name || ' ' || c.last_name AS name,
    c.orders_count,
    c.total_spent,
    c.total_spent / NULLIF(c.orders_count, 0) AS avg_order_value
FROM customers c
ORDER BY c.total_spent DESC
LIMIT 20;""",
            },
            {
                "description": "Orders pending fulfillment",
                "sql": """SELECT
    o.order_number,
    c.email,
    o.total_price,
    o.created_at
FROM orders o
LEFT JOIN customers c ON c.id = o.customer_id
WHERE o.fulfillment_status IS NULL
   OR o.fulfillment_status = 'partial'
ORDER BY o.created_at ASC;""",
            },
        ],
    },
    "twitter": {
        "is_ui": True,
        "ui_type": "Twitter / X Mobile App",
        "confidence": 0.95,
        "description": "Twitter/X mobile app showing tweet feed, user profiles, and social interaction features.",
        "entities": [
            {
                "name": "users",
                "description": "User accounts and profile information",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "username", "type": "VARCHAR(50)", "constraints": "UNIQUE NOT NULL"},
                    {"name": "display_name", "type": "VARCHAR(100)", "constraints": "NOT NULL"},
                    {"name": "bio", "type": "VARCHAR(160)", "constraints": ""},
                    {"name": "location", "type": "VARCHAR(100)", "constraints": ""},
                    {"name": "website_url", "type": "VARCHAR(500)", "constraints": ""},
                    {"name": "profile_image_url", "type": "VARCHAR(500)", "constraints": ""},
                    {"name": "banner_image_url", "type": "VARCHAR(500)", "constraints": ""},
                    {"name": "followers_count", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "following_count", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "tweet_count", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "verified", "type": "BOOLEAN", "constraints": "DEFAULT FALSE"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "tweets",
                "description": "Individual tweet posts with content and metadata",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "user_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES users(id)"},
                    {"name": "content", "type": "VARCHAR(280)", "constraints": "NOT NULL"},
                    {"name": "reply_to_tweet_id", "type": "INTEGER", "constraints": "REFERENCES tweets(id)"},
                    {"name": "retweet_of_id", "type": "INTEGER", "constraints": "REFERENCES tweets(id)"},
                    {"name": "quote_tweet_id", "type": "INTEGER", "constraints": "REFERENCES tweets(id)"},
                    {"name": "like_count", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "retweet_count", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "reply_count", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "view_count", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "is_sensitive", "type": "BOOLEAN", "constraints": "DEFAULT FALSE"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "follows",
                "description": "User follow relationships",
                "fields": [
                    {"name": "follower_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES users(id)"},
                    {"name": "following_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES users(id)"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "likes",
                "description": "Tweet likes/hearts by users",
                "fields": [
                    {"name": "user_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES users(id)"},
                    {"name": "tweet_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES tweets(id)"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "hashtags",
                "description": "Hashtag catalog",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "tag", "type": "VARCHAR(100)", "constraints": "UNIQUE NOT NULL"},
                    {"name": "tweet_count", "type": "INTEGER", "constraints": "DEFAULT 0"},
                ],
            },
            {
                "name": "tweet_hashtags",
                "description": "Many-to-many: tweets and hashtags",
                "fields": [
                    {"name": "tweet_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES tweets(id)"},
                    {"name": "hashtag_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES hashtags(id)"},
                ],
            },
        ],
        "sample_queries": [
            {
                "description": "Trending hashtags in the last 24 hours",
                "sql": """SELECT
    h.tag,
    COUNT(th.tweet_id) AS mentions
FROM hashtags h
JOIN tweet_hashtags th ON th.hashtag_id = h.id
JOIN tweets t ON t.id = th.tweet_id
WHERE t.created_at >= datetime('now', '-1 day')
GROUP BY h.id, h.tag
ORDER BY mentions DESC
LIMIT 10;""",
            },
            {
                "description": "Most engaged tweets",
                "sql": """SELECT
    u.username,
    t.content,
    t.like_count,
    t.retweet_count,
    t.reply_count,
    (t.like_count + t.retweet_count * 2 + t.reply_count) AS engagement_score
FROM tweets t
JOIN users u ON u.id = t.user_id
WHERE t.reply_to_tweet_id IS NULL
ORDER BY engagement_score DESC
LIMIT 20;""",
            },
            {
                "description": "Users with highest follower-to-following ratio",
                "sql": """SELECT
    username,
    display_name,
    followers_count,
    following_count,
    ROUND(CAST(followers_count AS FLOAT) / NULLIF(following_count, 0), 2) AS ratio
FROM users
WHERE followers_count > 1000
ORDER BY ratio DESC
LIMIT 10;""",
            },
        ],
    },
    "notion": {
        "is_ui": True,
        "ui_type": "Notion Workspace",
        "confidence": 0.94,
        "description": "Notion workspace showing pages, databases, blocks, and collaborative workspace structure.",
        "entities": [
            {
                "name": "workspaces",
                "description": "Top-level workspace containers",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "name", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "icon", "type": "VARCHAR(100)", "constraints": ""},
                    {"name": "domain", "type": "VARCHAR(100)", "constraints": "UNIQUE"},
                    {"name": "plan", "type": "VARCHAR(50)", "constraints": "DEFAULT 'free'"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "pages",
                "description": "Pages and sub-pages in the workspace",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "workspace_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES workspaces(id)"},
                    {"name": "parent_page_id", "type": "INTEGER", "constraints": "REFERENCES pages(id)"},
                    {"name": "title", "type": "VARCHAR(500)", "constraints": ""},
                    {"name": "icon", "type": "VARCHAR(100)", "constraints": ""},
                    {"name": "cover_url", "type": "VARCHAR(500)", "constraints": ""},
                    {"name": "is_database", "type": "BOOLEAN", "constraints": "DEFAULT FALSE"},
                    {"name": "archived", "type": "BOOLEAN", "constraints": "DEFAULT FALSE"},
                    {"name": "created_by", "type": "INTEGER", "constraints": "REFERENCES users(id)"},
                    {"name": "last_edited_by", "type": "INTEGER", "constraints": "REFERENCES users(id)"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                    {"name": "updated_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "blocks",
                "description": "Content blocks within pages",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "page_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES pages(id)"},
                    {"name": "parent_block_id", "type": "INTEGER", "constraints": "REFERENCES blocks(id)"},
                    {"name": "block_type", "type": "VARCHAR(50)", "constraints": "NOT NULL"},
                    {"name": "content", "type": "TEXT", "constraints": ""},
                    {"name": "properties", "type": "TEXT", "constraints": ""},
                    {"name": "sort_order", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
        ],
        "sample_queries": [
            {
                "description": "Pages with most sub-pages",
                "sql": """SELECT
    p.title,
    COUNT(child.id) AS subpage_count
FROM pages p
LEFT JOIN pages child ON child.parent_page_id = p.id
WHERE p.parent_page_id IS NULL
GROUP BY p.id, p.title
ORDER BY subpage_count DESC;""",
            },
        ],
    },
    "github": {
        "is_ui": True,
        "ui_type": "GitHub Repository",
        "confidence": 0.96,
        "description": "GitHub repository view showing pull requests, issues, commits, and contributor activity.",
        "entities": [
            {
                "name": "repositories",
                "description": "Git repositories with metadata",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "owner_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES users(id)"},
                    {"name": "name", "type": "VARCHAR(100)", "constraints": "NOT NULL"},
                    {"name": "full_name", "type": "VARCHAR(200)", "constraints": "UNIQUE NOT NULL"},
                    {"name": "description", "type": "TEXT", "constraints": ""},
                    {"name": "is_private", "type": "BOOLEAN", "constraints": "DEFAULT FALSE"},
                    {"name": "default_branch", "type": "VARCHAR(100)", "constraints": "DEFAULT 'main'"},
                    {"name": "stars_count", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "forks_count", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "open_issues_count", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "language", "type": "VARCHAR(50)", "constraints": ""},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                    {"name": "updated_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "users",
                "description": "GitHub user accounts",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "login", "type": "VARCHAR(39)", "constraints": "UNIQUE NOT NULL"},
                    {"name": "name", "type": "VARCHAR(255)", "constraints": ""},
                    {"name": "email", "type": "VARCHAR(255)", "constraints": ""},
                    {"name": "avatar_url", "type": "VARCHAR(500)", "constraints": ""},
                    {"name": "bio", "type": "TEXT", "constraints": ""},
                    {"name": "public_repos", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "followers", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "following", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "pull_requests",
                "description": "Pull requests against repository branches",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "repo_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES repositories(id)"},
                    {"name": "number", "type": "INTEGER", "constraints": "NOT NULL"},
                    {"name": "title", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "body", "type": "TEXT", "constraints": ""},
                    {"name": "state", "type": "VARCHAR(20)", "constraints": "DEFAULT 'open'"},
                    {"name": "author_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES users(id)"},
                    {"name": "head_branch", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "base_branch", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "merged", "type": "BOOLEAN", "constraints": "DEFAULT FALSE"},
                    {"name": "merged_at", "type": "TIMESTAMP", "constraints": ""},
                    {"name": "comments_count", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "commits_count", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "additions", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "deletions", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                    {"name": "updated_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "issues",
                "description": "Repository issues and bug reports",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "repo_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES repositories(id)"},
                    {"name": "number", "type": "INTEGER", "constraints": "NOT NULL"},
                    {"name": "title", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "body", "type": "TEXT", "constraints": ""},
                    {"name": "state", "type": "VARCHAR(20)", "constraints": "DEFAULT 'open'"},
                    {"name": "author_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES users(id)"},
                    {"name": "assignee_id", "type": "INTEGER", "constraints": "REFERENCES users(id)"},
                    {"name": "comments_count", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                    {"name": "closed_at", "type": "TIMESTAMP", "constraints": ""},
                ],
            },
        ],
        "sample_queries": [
            {
                "description": "Open pull requests by author with review stats",
                "sql": """SELECT
    u.login,
    COUNT(pr.id) AS open_prs,
    SUM(pr.additions) AS lines_added,
    SUM(pr.deletions) AS lines_removed
FROM pull_requests pr
JOIN users u ON u.id = pr.author_id
WHERE pr.state = 'open'
GROUP BY u.id, u.login
ORDER BY open_prs DESC;""",
            },
            {
                "description": "Most active repositories by issue count",
                "sql": """SELECT
    r.full_name,
    r.language,
    r.stars_count,
    COUNT(i.id) AS total_issues,
    SUM(CASE WHEN i.state = 'open' THEN 1 ELSE 0 END) AS open_issues
FROM repositories r
LEFT JOIN issues i ON i.repo_id = r.id
GROUP BY r.id
ORDER BY total_issues DESC
LIMIT 10;""",
            },
            {
                "description": "PR merge rate by repository",
                "sql": """SELECT
    r.full_name,
    COUNT(pr.id) AS total_prs,
    SUM(CASE WHEN pr.merged THEN 1 ELSE 0 END) AS merged_prs,
    ROUND(100.0 * SUM(CASE WHEN pr.merged THEN 1 ELSE 0 END) / COUNT(pr.id), 1) AS merge_rate_pct
FROM repositories r
JOIN pull_requests pr ON pr.repo_id = r.id
GROUP BY r.id
HAVING total_prs >= 5
ORDER BY merge_rate_pct DESC;""",
            },
        ],
    },
    "slack": {
        "is_ui": True,
        "ui_type": "Slack Workspace",
        "confidence": 0.95,
        "description": "Slack messaging workspace showing channels, direct messages, and user activity.",
        "entities": [
            {
                "name": "workspaces",
                "description": "Slack workspace (organization) accounts",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "name", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "domain", "type": "VARCHAR(100)", "constraints": "UNIQUE NOT NULL"},
                    {"name": "icon_url", "type": "VARCHAR(500)", "constraints": ""},
                    {"name": "plan", "type": "VARCHAR(50)", "constraints": "DEFAULT 'free'"},
                    {"name": "member_count", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "users",
                "description": "Workspace members and their profile data",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "workspace_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES workspaces(id)"},
                    {"name": "username", "type": "VARCHAR(80)", "constraints": "NOT NULL"},
                    {"name": "display_name", "type": "VARCHAR(80)", "constraints": ""},
                    {"name": "real_name", "type": "VARCHAR(255)", "constraints": ""},
                    {"name": "email", "type": "VARCHAR(255)", "constraints": "UNIQUE"},
                    {"name": "avatar_url", "type": "VARCHAR(500)", "constraints": ""},
                    {"name": "status_text", "type": "VARCHAR(100)", "constraints": ""},
                    {"name": "status_emoji", "type": "VARCHAR(50)", "constraints": ""},
                    {"name": "is_admin", "type": "BOOLEAN", "constraints": "DEFAULT FALSE"},
                    {"name": "is_bot", "type": "BOOLEAN", "constraints": "DEFAULT FALSE"},
                    {"name": "timezone", "type": "VARCHAR(50)", "constraints": ""},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "channels",
                "description": "Public and private channels within a workspace",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "workspace_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES workspaces(id)"},
                    {"name": "name", "type": "VARCHAR(80)", "constraints": "NOT NULL"},
                    {"name": "topic", "type": "VARCHAR(250)", "constraints": ""},
                    {"name": "purpose", "type": "VARCHAR(250)", "constraints": ""},
                    {"name": "is_private", "type": "BOOLEAN", "constraints": "DEFAULT FALSE"},
                    {"name": "is_archived", "type": "BOOLEAN", "constraints": "DEFAULT FALSE"},
                    {"name": "creator_id", "type": "INTEGER", "constraints": "REFERENCES users(id)"},
                    {"name": "member_count", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "messages",
                "description": "Chat messages in channels and DMs",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "channel_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES channels(id)"},
                    {"name": "user_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES users(id)"},
                    {"name": "text", "type": "TEXT", "constraints": ""},
                    {"name": "thread_ts", "type": "VARCHAR(20)", "constraints": ""},
                    {"name": "reply_count", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "reaction_count", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "is_edited", "type": "BOOLEAN", "constraints": "DEFAULT FALSE"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
        ],
        "sample_queries": [
            {
                "description": "Most active channels by message volume (last 30 days)",
                "sql": """SELECT
    c.name,
    c.member_count,
    COUNT(m.id) AS messages_30d
FROM channels c
JOIN messages m ON m.channel_id = c.id
WHERE m.created_at >= datetime('now', '-30 days')
  AND c.is_archived = FALSE
GROUP BY c.id, c.name
ORDER BY messages_30d DESC
LIMIT 15;""",
            },
            {
                "description": "Top contributors per channel",
                "sql": """SELECT
    c.name AS channel,
    u.display_name AS user,
    COUNT(m.id) AS message_count
FROM messages m
JOIN channels c ON c.id = m.channel_id
JOIN users u ON u.id = m.user_id
WHERE u.is_bot = FALSE
GROUP BY c.id, u.id
ORDER BY c.name, message_count DESC;""",
            },
        ],
    },
    "stripe": {
        "is_ui": True,
        "ui_type": "Stripe Dashboard",
        "confidence": 0.96,
        "description": "Stripe payments dashboard showing customers, subscriptions, invoices, and payment intents.",
        "entities": [
            {
                "name": "customers",
                "description": "Stripe customer accounts",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "stripe_id", "type": "VARCHAR(50)", "constraints": "UNIQUE NOT NULL"},
                    {"name": "email", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "name", "type": "VARCHAR(255)", "constraints": ""},
                    {"name": "phone", "type": "VARCHAR(20)", "constraints": ""},
                    {"name": "currency", "type": "VARCHAR(3)", "constraints": "DEFAULT 'usd'"},
                    {"name": "balance", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "delinquent", "type": "BOOLEAN", "constraints": "DEFAULT FALSE"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "products",
                "description": "Billing products and plans",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "stripe_id", "type": "VARCHAR(50)", "constraints": "UNIQUE NOT NULL"},
                    {"name": "name", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "description", "type": "TEXT", "constraints": ""},
                    {"name": "active", "type": "BOOLEAN", "constraints": "DEFAULT TRUE"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "prices",
                "description": "Pricing options for products (recurring or one-time)",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "stripe_id", "type": "VARCHAR(50)", "constraints": "UNIQUE NOT NULL"},
                    {"name": "product_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES products(id)"},
                    {"name": "currency", "type": "VARCHAR(3)", "constraints": "NOT NULL"},
                    {"name": "unit_amount", "type": "INTEGER", "constraints": "NOT NULL"},
                    {"name": "recurring_interval", "type": "VARCHAR(10)", "constraints": ""},
                    {"name": "active", "type": "BOOLEAN", "constraints": "DEFAULT TRUE"},
                ],
            },
            {
                "name": "subscriptions",
                "description": "Customer subscriptions to products",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "stripe_id", "type": "VARCHAR(50)", "constraints": "UNIQUE NOT NULL"},
                    {"name": "customer_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES customers(id)"},
                    {"name": "price_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES prices(id)"},
                    {"name": "status", "type": "VARCHAR(30)", "constraints": "NOT NULL"},
                    {"name": "current_period_start", "type": "TIMESTAMP", "constraints": ""},
                    {"name": "current_period_end", "type": "TIMESTAMP", "constraints": ""},
                    {"name": "cancel_at_period_end", "type": "BOOLEAN", "constraints": "DEFAULT FALSE"},
                    {"name": "canceled_at", "type": "TIMESTAMP", "constraints": ""},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "payment_intents",
                "description": "Individual payment attempts and their status",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "stripe_id", "type": "VARCHAR(50)", "constraints": "UNIQUE NOT NULL"},
                    {"name": "customer_id", "type": "INTEGER", "constraints": "REFERENCES customers(id)"},
                    {"name": "amount", "type": "INTEGER", "constraints": "NOT NULL"},
                    {"name": "currency", "type": "VARCHAR(3)", "constraints": "NOT NULL"},
                    {"name": "status", "type": "VARCHAR(30)", "constraints": "NOT NULL"},
                    {"name": "description", "type": "TEXT", "constraints": ""},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
        ],
        "sample_queries": [
            {
                "description": "Monthly recurring revenue (MRR) by plan",
                "sql": """SELECT
    pr.name AS plan,
    COUNT(s.id) AS active_subscribers,
    SUM(p.unit_amount) / 100.0 AS mrr_usd
FROM subscriptions s
JOIN prices p ON p.id = s.price_id
JOIN products pr ON pr.id = p.product_id
WHERE s.status = 'active'
  AND p.recurring_interval = 'month'
GROUP BY pr.id, pr.name
ORDER BY mrr_usd DESC;""",
            },
            {
                "description": "Churn analysis — subscriptions canceled in last 90 days",
                "sql": """SELECT
    DATE(s.canceled_at) AS cancel_date,
    COUNT(*) AS cancellations,
    SUM(p.unit_amount) / 100.0 AS lost_mrr_usd
FROM subscriptions s
JOIN prices p ON p.id = s.price_id
WHERE s.canceled_at >= datetime('now', '-90 days')
GROUP BY DATE(s.canceled_at)
ORDER BY cancel_date DESC;""",
            },
            {
                "description": "Payment success rate by currency",
                "sql": """SELECT
    currency,
    COUNT(*) AS total,
    SUM(CASE WHEN status = 'succeeded' THEN 1 ELSE 0 END) AS succeeded,
    ROUND(100.0 * SUM(CASE WHEN status = 'succeeded' THEN 1 ELSE 0 END) / COUNT(*), 1) AS success_rate
FROM payment_intents
GROUP BY currency
ORDER BY total DESC;""",
            },
        ],
    },
    "linear": {
        "is_ui": True,
        "ui_type": "Linear Issue Tracker",
        "confidence": 0.94,
        "description": "Linear project management tool showing teams, projects, cycles, and issue tracking.",
        "entities": [
            {
                "name": "teams",
                "description": "Engineering teams within the organization",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "name", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "key", "type": "VARCHAR(10)", "constraints": "UNIQUE NOT NULL"},
                    {"name": "description", "type": "TEXT", "constraints": ""},
                    {"name": "color", "type": "VARCHAR(7)", "constraints": ""},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "members",
                "description": "Team members and workspace users",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "name", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "email", "type": "VARCHAR(255)", "constraints": "UNIQUE NOT NULL"},
                    {"name": "display_name", "type": "VARCHAR(100)", "constraints": ""},
                    {"name": "avatar_url", "type": "VARCHAR(500)", "constraints": ""},
                    {"name": "is_admin", "type": "BOOLEAN", "constraints": "DEFAULT FALSE"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "projects",
                "description": "Projects grouping related issues",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "team_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES teams(id)"},
                    {"name": "name", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "description", "type": "TEXT", "constraints": ""},
                    {"name": "status", "type": "VARCHAR(50)", "constraints": "DEFAULT 'planned'"},
                    {"name": "progress", "type": "DECIMAL(5,2)", "constraints": "DEFAULT 0"},
                    {"name": "target_date", "type": "TIMESTAMP", "constraints": ""},
                    {"name": "lead_id", "type": "INTEGER", "constraints": "REFERENCES members(id)"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "issues",
                "description": "Individual work items and bugs",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "team_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES teams(id)"},
                    {"name": "project_id", "type": "INTEGER", "constraints": "REFERENCES projects(id)"},
                    {"name": "identifier", "type": "VARCHAR(20)", "constraints": "UNIQUE NOT NULL"},
                    {"name": "title", "type": "VARCHAR(512)", "constraints": "NOT NULL"},
                    {"name": "description", "type": "TEXT", "constraints": ""},
                    {"name": "state", "type": "VARCHAR(50)", "constraints": "DEFAULT 'backlog'"},
                    {"name": "priority", "type": "INTEGER", "constraints": "DEFAULT 0"},
                    {"name": "assignee_id", "type": "INTEGER", "constraints": "REFERENCES members(id)"},
                    {"name": "creator_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES members(id)"},
                    {"name": "estimate", "type": "DECIMAL(4,1)", "constraints": ""},
                    {"name": "due_date", "type": "TIMESTAMP", "constraints": ""},
                    {"name": "completed_at", "type": "TIMESTAMP", "constraints": ""},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
        ],
        "sample_queries": [
            {
                "description": "Issue throughput by team (completed per week)",
                "sql": """SELECT
    t.name AS team,
    strftime('%Y-W%W', i.completed_at) AS week,
    COUNT(*) AS issues_completed
FROM issues i
JOIN teams t ON t.id = i.team_id
WHERE i.completed_at IS NOT NULL
  AND i.completed_at >= datetime('now', '-90 days')
GROUP BY t.id, week
ORDER BY week DESC, issues_completed DESC;""",
            },
            {
                "description": "Backlog health — unassigned high-priority issues",
                "sql": """SELECT
    t.name AS team,
    i.identifier,
    i.title,
    i.priority,
    i.created_at,
    julianday('now') - julianday(i.created_at) AS age_days
FROM issues i
JOIN teams t ON t.id = i.team_id
WHERE i.assignee_id IS NULL
  AND i.priority <= 2
  AND i.state NOT IN ('done', 'cancelled')
ORDER BY i.priority ASC, age_days DESC;""",
            },
        ],
    },
    "jira": {
        "is_ui": True,
        "ui_type": "Jira Project Management",
        "confidence": 0.94,
        "description": "Jira project board showing issues, sprints, epics, and team workflow.",
        "entities": [
            {
                "name": "projects",
                "description": "Jira projects grouping related work",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "key", "type": "VARCHAR(10)", "constraints": "UNIQUE NOT NULL"},
                    {"name": "name", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "description", "type": "TEXT", "constraints": ""},
                    {"name": "project_type", "type": "VARCHAR(50)", "constraints": "DEFAULT 'software'"},
                    {"name": "lead_id", "type": "INTEGER", "constraints": "REFERENCES users(id)"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "users",
                "description": "Jira user accounts",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "account_id", "type": "VARCHAR(100)", "constraints": "UNIQUE NOT NULL"},
                    {"name": "email", "type": "VARCHAR(255)", "constraints": "UNIQUE NOT NULL"},
                    {"name": "display_name", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "avatar_url", "type": "VARCHAR(500)", "constraints": ""},
                    {"name": "active", "type": "BOOLEAN", "constraints": "DEFAULT TRUE"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "sprints",
                "description": "Sprint iterations for agile planning",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "project_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES projects(id)"},
                    {"name": "name", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "goal", "type": "TEXT", "constraints": ""},
                    {"name": "state", "type": "VARCHAR(20)", "constraints": "DEFAULT 'future'"},
                    {"name": "start_date", "type": "TIMESTAMP", "constraints": ""},
                    {"name": "end_date", "type": "TIMESTAMP", "constraints": ""},
                    {"name": "complete_date", "type": "TIMESTAMP", "constraints": ""},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "issues",
                "description": "Jira issues — stories, bugs, tasks, epics",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "project_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES projects(id)"},
                    {"name": "sprint_id", "type": "INTEGER", "constraints": "REFERENCES sprints(id)"},
                    {"name": "key", "type": "VARCHAR(20)", "constraints": "UNIQUE NOT NULL"},
                    {"name": "summary", "type": "VARCHAR(512)", "constraints": "NOT NULL"},
                    {"name": "description", "type": "TEXT", "constraints": ""},
                    {"name": "issue_type", "type": "VARCHAR(50)", "constraints": "DEFAULT 'Story'"},
                    {"name": "status", "type": "VARCHAR(50)", "constraints": "DEFAULT 'To Do'"},
                    {"name": "priority", "type": "VARCHAR(20)", "constraints": "DEFAULT 'Medium'"},
                    {"name": "assignee_id", "type": "INTEGER", "constraints": "REFERENCES users(id)"},
                    {"name": "reporter_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES users(id)"},
                    {"name": "story_points", "type": "DECIMAL(4,1)", "constraints": ""},
                    {"name": "parent_id", "type": "INTEGER", "constraints": "REFERENCES issues(id)"},
                    {"name": "due_date", "type": "TIMESTAMP", "constraints": ""},
                    {"name": "resolved_at", "type": "TIMESTAMP", "constraints": ""},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                    {"name": "updated_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
        ],
        "sample_queries": [
            {
                "description": "Sprint velocity — story points completed per sprint",
                "sql": """SELECT
    s.name AS sprint,
    s.start_date,
    COUNT(i.id) AS issues_completed,
    SUM(i.story_points) AS velocity
FROM sprints s
JOIN issues i ON i.sprint_id = s.id
WHERE i.status = 'Done'
  AND s.state = 'closed'
GROUP BY s.id
ORDER BY s.start_date DESC
LIMIT 10;""",
            },
            {
                "description": "Open bugs by priority with age",
                "sql": """SELECT
    i.priority,
    COUNT(*) AS open_count,
    AVG(julianday('now') - julianday(i.created_at)) AS avg_age_days
FROM issues i
WHERE i.issue_type = 'Bug'
  AND i.status NOT IN ('Done', 'Closed', 'Resolved')
GROUP BY i.priority
ORDER BY CASE i.priority
    WHEN 'Highest' THEN 1 WHEN 'High' THEN 2
    WHEN 'Medium' THEN 3 WHEN 'Low' THEN 4 ELSE 5 END;""",
            },
        ],
    },
    "figma": {
        "is_ui": True,
        "ui_type": "Figma Design Tool",
        "confidence": 0.91,
        "description": "Figma design workspace showing projects, files, components, and team collaboration.",
        "entities": [
            {
                "name": "teams",
                "description": "Figma teams grouping collaborators",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "name", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "description", "type": "TEXT", "constraints": ""},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "users",
                "description": "Figma user accounts",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "email", "type": "VARCHAR(255)", "constraints": "UNIQUE NOT NULL"},
                    {"name": "handle", "type": "VARCHAR(100)", "constraints": "UNIQUE NOT NULL"},
                    {"name": "name", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "avatar_url", "type": "VARCHAR(500)", "constraints": ""},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "projects",
                "description": "Design projects containing files",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "team_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES teams(id)"},
                    {"name": "name", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "files",
                "description": "Design files within a project",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "project_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES projects(id)"},
                    {"name": "name", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "key", "type": "VARCHAR(100)", "constraints": "UNIQUE NOT NULL"},
                    {"name": "thumbnail_url", "type": "VARCHAR(500)", "constraints": ""},
                    {"name": "last_modified", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "components",
                "description": "Reusable design components",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "file_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES files(id)"},
                    {"name": "name", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "description", "type": "TEXT", "constraints": ""},
                    {"name": "node_id", "type": "VARCHAR(100)", "constraints": "NOT NULL"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                    {"name": "updated_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
        ],
        "sample_queries": [
            {
                "description": "Most recently modified files per project",
                "sql": """SELECT
    p.name AS project,
    f.name AS file,
    f.last_modified
FROM files f
JOIN projects p ON p.id = f.project_id
ORDER BY f.last_modified DESC
LIMIT 20;""",
            },
            {
                "description": "Component library size by file",
                "sql": """SELECT
    f.name AS file,
    COUNT(c.id) AS component_count
FROM components c
JOIN files f ON f.id = c.file_id
GROUP BY f.id, f.name
ORDER BY component_count DESC;""",
            },
        ],
    },
    "airtable": {
        "is_ui": True,
        "ui_type": "Airtable Base",
        "confidence": 0.92,
        "description": "Airtable base showing tables, fields, records, and collaborative workspace.",
        "entities": [
            {
                "name": "workspaces",
                "description": "Top-level Airtable workspaces",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "name", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "owner_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES users(id)"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "users",
                "description": "Airtable user accounts",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "email", "type": "VARCHAR(255)", "constraints": "UNIQUE NOT NULL"},
                    {"name": "name", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "bases",
                "description": "Airtable bases (databases) within a workspace",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "workspace_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES workspaces(id)"},
                    {"name": "name", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "color", "type": "VARCHAR(50)", "constraints": ""},
                    {"name": "icon", "type": "VARCHAR(100)", "constraints": ""},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "base_tables",
                "description": "Tables within an Airtable base",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "base_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES bases(id)"},
                    {"name": "name", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "description", "type": "TEXT", "constraints": ""},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "table_fields",
                "description": "Column field definitions for each base table",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "table_id", "type": "INTEGER", "constraints": "NOT NULL REFERENCES base_tables(id)"},
                    {"name": "name", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "field_type", "type": "VARCHAR(50)", "constraints": "NOT NULL"},
                    {"name": "options", "type": "TEXT", "constraints": ""},
                    {"name": "position", "type": "INTEGER", "constraints": "DEFAULT 0"},
                ],
            },
        ],
        "sample_queries": [
            {
                "description": "Tables with most fields per base",
                "sql": """SELECT
    b.name AS base,
    t.name AS table_name,
    COUNT(f.id) AS field_count
FROM base_tables t
JOIN bases b ON b.id = t.base_id
JOIN table_fields f ON f.table_id = t.id
GROUP BY t.id, b.name, t.name
ORDER BY field_count DESC
LIMIT 20;""",
            },
            {
                "description": "Field type distribution across all tables",
                "sql": """SELECT
    f.field_type,
    COUNT(*) AS count
FROM table_fields f
GROUP BY f.field_type
ORDER BY count DESC;""",
            },
        ],
    },
    "hubspot": {
        "is_ui": True,
        "ui_type": "HubSpot CRM",
        "confidence": 0.93,
        "description": "HubSpot CRM showing contacts, companies, deals, and pipeline management.",
        "entities": [
            {
                "name": "contacts",
                "description": "CRM contacts — individual people",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "email", "type": "VARCHAR(255)", "constraints": "UNIQUE NOT NULL"},
                    {"name": "first_name", "type": "VARCHAR(100)", "constraints": ""},
                    {"name": "last_name", "type": "VARCHAR(100)", "constraints": ""},
                    {"name": "phone", "type": "VARCHAR(30)", "constraints": ""},
                    {"name": "job_title", "type": "VARCHAR(255)", "constraints": ""},
                    {"name": "lifecycle_stage", "type": "VARCHAR(50)", "constraints": "DEFAULT 'lead'"},
                    {"name": "lead_status", "type": "VARCHAR(50)", "constraints": ""},
                    {"name": "owner_id", "type": "INTEGER", "constraints": "REFERENCES users(id)"},
                    {"name": "company_id", "type": "INTEGER", "constraints": "REFERENCES companies(id)"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                    {"name": "updated_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "companies",
                "description": "Companies/accounts in the CRM",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "name", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "domain", "type": "VARCHAR(255)", "constraints": "UNIQUE"},
                    {"name": "industry", "type": "VARCHAR(100)", "constraints": ""},
                    {"name": "num_employees", "type": "INTEGER", "constraints": ""},
                    {"name": "annual_revenue", "type": "DECIMAL(15,2)", "constraints": ""},
                    {"name": "city", "type": "VARCHAR(100)", "constraints": ""},
                    {"name": "country", "type": "VARCHAR(100)", "constraints": ""},
                    {"name": "owner_id", "type": "INTEGER", "constraints": "REFERENCES users(id)"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "users",
                "description": "HubSpot portal users / sales reps",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "email", "type": "VARCHAR(255)", "constraints": "UNIQUE NOT NULL"},
                    {"name": "first_name", "type": "VARCHAR(100)", "constraints": ""},
                    {"name": "last_name", "type": "VARCHAR(100)", "constraints": ""},
                    {"name": "role", "type": "VARCHAR(50)", "constraints": "DEFAULT 'sales_rep'"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
            {
                "name": "deals",
                "description": "Sales deals and pipeline opportunities",
                "fields": [
                    {"name": "id", "type": "INTEGER", "constraints": "PRIMARY KEY AUTOINCREMENT"},
                    {"name": "name", "type": "VARCHAR(255)", "constraints": "NOT NULL"},
                    {"name": "owner_id", "type": "INTEGER", "constraints": "REFERENCES users(id)"},
                    {"name": "company_id", "type": "INTEGER", "constraints": "REFERENCES companies(id)"},
                    {"name": "contact_id", "type": "INTEGER", "constraints": "REFERENCES contacts(id)"},
                    {"name": "pipeline_stage", "type": "VARCHAR(100)", "constraints": "NOT NULL"},
                    {"name": "amount", "type": "DECIMAL(15,2)", "constraints": ""},
                    {"name": "close_date", "type": "TIMESTAMP", "constraints": ""},
                    {"name": "deal_type", "type": "VARCHAR(50)", "constraints": ""},
                    {"name": "is_closed", "type": "BOOLEAN", "constraints": "DEFAULT FALSE"},
                    {"name": "is_won", "type": "BOOLEAN", "constraints": "DEFAULT FALSE"},
                    {"name": "created_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                    {"name": "updated_at", "type": "TIMESTAMP", "constraints": "DEFAULT CURRENT_TIMESTAMP"},
                ],
            },
        ],
        "sample_queries": [
            {
                "description": "Pipeline value by stage",
                "sql": """SELECT
    d.pipeline_stage,
    COUNT(*) AS deal_count,
    SUM(d.amount) AS total_value,
    AVG(d.amount) AS avg_deal_size
FROM deals d
WHERE d.is_closed = FALSE
GROUP BY d.pipeline_stage
ORDER BY total_value DESC;""",
            },
            {
                "description": "Top sales reps by closed-won revenue this quarter",
                "sql": """SELECT
    u.first_name || ' ' || u.last_name AS rep,
    COUNT(*) AS deals_won,
    SUM(d.amount) AS revenue
FROM deals d
JOIN users u ON u.id = d.owner_id
WHERE d.is_won = TRUE
  AND d.close_date >= date('now', 'start of month', '-2 months')
GROUP BY u.id
ORDER BY revenue DESC
LIMIT 10;""",
            },
        ],
    },
    "no_ui": {
        "is_ui": False,
        "ui_type": None,
        "confidence": 0.02,
        "description": "This image does not appear to contain a software user interface. It looks like a nature or non-UI photograph.",
        "entities": [],
        "sample_queries": [],
        "error": "No UI detected. Please upload a screenshot of a software application.",
    },
}

KEYWORD_MAPPINGS = {
    "shopify": "shopify",
    "shop": "shopify",
    "ecommerce": "shopify",
    "product": "shopify",
    "order": "shopify",
    "twitter": "twitter",
    "tweet": "twitter",
    "x.com": "twitter",
    "social": "twitter",
    "notion": "notion",
    "wiki": "notion",
    "github": "github",
    "pull request": "github",
    "repository": "github",
    "repo": "github",
    "commit": "github",
    "slack": "slack",
    "channel": "slack",
    "workspace": "slack",
    "stripe": "stripe",
    "payment": "stripe",
    "subscription": "stripe",
    "invoice": "stripe",
    "billing": "stripe",
    "linear": "linear",
    "issue tracker": "linear",
    "sprint": "linear",
    "backlog": "linear",
    "jira": "jira",
    "atlassian": "jira",
    "epic": "jira",
    "story point": "jira",
    "figma": "figma",
    "design tool": "figma",
    "component library": "figma",
    "wireframe": "figma",
    "prototype": "figma",
    "airtable": "airtable",
    "base": "airtable",
    "hubspot": "hubspot",
    "crm": "hubspot",
    "pipeline": "hubspot",
    "deal": "hubspot",
    "sales": "hubspot",
    "nature": "no_ui",
    "landscape": "no_ui",
    "photo": "no_ui",
    "animal": "no_ui",
    "forest": "no_ui",
    "mountain": "no_ui",
    "beach": "no_ui",
    "default": "shopify",
}

# Alias so MOCK_RESPONSES["default"] works as a fallback in analyzer.py
MOCK_RESPONSES["default"] = MOCK_RESPONSES["shopify"]
