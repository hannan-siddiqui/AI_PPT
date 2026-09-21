"""
Sample JSON datasets for instant demonstration and testing.
"""

SAMPLE_TEMPLATES = {
    "pitch_deck": {
        "name": "SaaS AI Startup Pitch Deck",
        "description": "High-growth Series A presentation with traction metrics and market sizing",
        "data": {
            "company_name": "NexusAI Cloud",
            "tagline": "Autonomous Enterprise Intelligence Infrastructure",
            "executive_summary": "Empowering Fortune 500 enterprises with self-optimizing multi-agent workflows.",
            "problem": [
                "Enterprise data remains trapped in legacy silos with poor interoperability",
                "Manual business workflows cost global knowledge enterprises over $320B annually",
                "Existing LLM integrations lack safety verification, latency controls, and ROI tracking"
            ],
            "solution": [
                "Real-time autonomic agent orchestrator deploying across hybrid cloud environments",
                "Deterministic verification engine reducing hallucination rates to below 0.01%",
                "Turnkey integration with SAP, Salesforce, Snowflake, and custom internal APIs"
            ],
            "traction_metrics": [
                {"label": "Annual Recurring Revenue", "value": "$4.8M", "growth": "+280% YoY"},
                {"label": "Enterprise Customers", "value": "142+", "growth": "98% Net Retention"},
                {"label": "Average Contract Value", "value": "$85K", "growth": "+45% ACV Lift"},
                {"label": "Gross Margins", "value": "84%", "growth": "Top Quartile SaaS"}
            ],
            "market_opportunity": {
                "tam": "$140 Billion (Enterprise AI & Automation by 2028)",
                "sam": "$42 Billion (Mid-to-Large Tier SaaS Automations)",
                "som": "$3.8 Billion (Addressable Tier 1 Initial Focus)"
            },
            "milestones": [
                {"quarter": "Q1 2025", "title": "Platform v2 Launch", "detail": "Launched multi-cloud low-latency router"},
                {"quarter": "Q3 2025", "title": "100th Enterprise Customer", "detail": "Crossed $3M ARR with zero customer churn"},
                {"quarter": "Q1 2026", "title": "Global Expansion", "detail": "Opened EMEA and APAC compliance hubs"},
                {"quarter": "Q4 2026", "title": "Autonomous Agents v3", "detail": "Targeting $15M ARR and SOC2 Type II certifications"}
            ],
            "ask": {
                "funding_target": "$12M Series A",
                "allocation": "60% Engineering & AI Research, 25% Go-To-Market Sales, 15% Strategic Partnerships"
            }
        }
    },
    "qbr": {
        "name": "Quarterly Business Review (QBR)",
        "description": "Comprehensive quarterly corporate executive performance summary",
        "data": {
            "period": "Q4 2025 & FY Strategic Review",
            "division": "Global Products & Revenue Operations",
            "highlights": [
                "Record performance exceeding top-line targets by 14.2% across core regions",
                "Customer satisfaction (CSAT) elevated to all-time high of 94.6%",
                "Successful rollout of automated onboarding reducing time-to-value from 28 to 9 days"
            ],
            "kpis": [
                {"label": "Quarterly Revenue", "value": "$28.4M", "growth": "+19.4% QoQ"},
                {"label": "Operating Margin", "value": "27.8%", "growth": "+320 bps"},
                {"label": "Active Users", "value": "1.4M", "growth": "+35% YoY"},
                {"label": "NPS Score", "value": "72", "growth": "Industry Benchmark: 55"}
            ],
            "key_initiatives": [
                {"title": "Supply Chain Resilience", "status": "Completed", "impact": "Saved $1.8M in freight logistics"},
                {"title": "Core Platform Modernization", "status": "In Progress", "impact": "99.995% uptime achieved"},
                {"title": "Enterprise Security Tier", "status": "Completed", "impact": "18 Fortune 100 pilots started"}
            ],
            "next_quarter_priorities": [
                "Scale direct sales motion in Western Europe and Japan",
                "Ship v3 product analytics engine with self-serve telemetry",
                "Attain ISO 27001 renewal and FedRAMP readiness milestone"
            ]
        }
    },
    "product_launch": {
        "name": "Product Launch Go-To-Market",
        "description": "Product strategy, persona targeting, value propositions, and launch roadmap",
        "data": {
            "product_name": "AetherDesk Pro",
            "positioning": "The next-generation collaborative workspace for distributed engineering teams",
            "target_personas": [
                {"role": "Engineering Leaders (VPs & Directors)", "focus": "Team velocity, blocker visibility, code quality"},
                {"role": "Staff Architects & Tech Leads", "focus": "System design reviews, architecture mapping"},
                {"role": "Full-Stack Developers", "focus": "Frictionless context switching, instant dev envs"}
            ],
            "core_features": [
                {"feature": "Instant Spatial Canvases", "benefit": "Collaborative real-time architectural whiteboard with live code sync"},
                {"feature": "AI Context Copilot", "benefit": "Auto-summarizes PRs, Jira tasks, and RFC decisions in seconds"},
                {"feature": "Zero-Config Micro-Envs", "benefit": "Spin up ephemeral staging environments with 1 click"}
            ],
            "launch_timeline": [
                {"phase": "Private Beta", "timing": "Month 1", "goal": "50 high-velocity design partner teams"},
                {"phase": "Public Preview", "timing": "Month 2", "goal": "Product Hunt #1 of the Day, 10,000 signups"},
                {"phase": "Enterprise GA", "timing": "Month 3", "goal": "SOC-2, SSO, dedicated VPC hosting available"}
            ],
            "success_metrics": [
                {"metric": "Monthly Active Teams", "target": "2,500 teams by Q3"},
                {"metric": "Weekly Retention", "target": "> 68% active cohort"},
                {"metric": "Organic Referral Rate", "target": "> 35% via workspace invites"}
            ]
        }
    },
    "mckinsey_boardroom": {
        "name": "McKinsey CXO Workforce Strategy",
        "description": "Boardroom workforce diversity, FTE headcount, and compensation equity analysis",
        "data": {
            "data": [
                {
                    "chart": {
                        "graphType": "stacked-bar",
                        "possible_chart_types": [
                            {"label": "Stacked Bar", "graphType": "stacked-bar"},
                            {"label": "Grouped Column", "graphType": "grouped-column", "isCalculated": 1},
                            {"label": "Heatmap", "graphType": "heatmap", "isCalculated": 1}
                        ],
                        "dimension": ["customString3", "gender"],
                        "labels": ["Renewables", "T&D"],
                        "datasets": {
                            "default": [
                                {"label": "Female", "data": [2184004.9, 0], "stack": "Stack 0"},
                                {"label": "Male", "data": [1741460.83, 1782511.13], "stack": "Stack 0"}
                            ]
                        },
                        "axisLabel": {"xAxis": "category", "yAxis": "Average Salary High Performer"}
                    }
                },
                {
                    "chart": {
                        "graphType": "stacked-bar",
                        "possible_chart_types": [
                            {"label": "Stacked Bar", "graphType": "stacked-bar"},
                            {"label": "Grouped Column", "graphType": "grouped-column", "isCalculated": 1},
                            {"label": "Heatmap", "graphType": "heatmap", "isCalculated": 1}
                        ],
                        "dimension": ["customString3", "gender"],
                        "labels": ["Corporate Functions & Internationals", "Generation", "Renewables", "T&D"],
                        "datasets": {
                            "default": [
                                {"label": "Female", "data": [150, 158, 288, 151], "stack": "Stack 0"},
                                {"label": "Male", "data": [254, 1188, 1665, 731], "stack": "Stack 0"}
                            ]
                        },
                        "axisLabel": {"xAxis": "category", "yAxis": "SOP FTE"}
                    }
                },
                {
                    "chart": {
                        "graphType": "stacked-bar",
                        "possible_chart_types": [
                            {"label": "Stacked Bar", "graphType": "stacked-bar"},
                            {"label": "Grouped Column", "graphType": "grouped-column", "isCalculated": 1},
                            {"label": "Heatmap", "graphType": "heatmap", "isCalculated": 1}
                        ],
                        "dimension": ["customString3", "gender"],
                        "labels": ["Corporate Functions & Internationals", "Generation", "Renewables", "T&D"],
                        "datasets": {
                            "default": [
                                {"label": "Female", "data": [150, 156, 295, 151], "stack": "Stack 0"},
                                {"label": "Male", "data": [253, 1185, 1668, 729], "stack": "Stack 0"}
                            ]
                        },
                        "axisLabel": {"xAxis": "category", "yAxis": "EOP Headcount"}
                    }
                }
            ],
            "n_slides": 8,
            "audience": "CXOs",
            "template": "neo-general",
            "theme": "mint-blue"
        }
    }
}
