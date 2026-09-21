"""
High-Design Presentation Generator using python-pptx
Produces modern 16:9 widescreen executive decks with custom themes,
card containers, KPI stat blocks, and image embedding.
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image

# 16:9 Widescreen dimensions
SLIDE_WIDTH_INCHES = 13.333
SLIDE_HEIGHT_INCHES = 7.5

def hex_to_rgb(hex_str: str) -> RGBColor:
    """Convert hex string (e.g. '#3B82F6' or '3B82F6') to RGBColor."""
    if not hex_str:
        return RGBColor(59, 130, 246)
    hex_clean = hex_str.lstrip('#')
    if len(hex_clean) == 3:
        hex_clean = ''.join([c*2 for c in hex_clean])
    if len(hex_clean) != 6:
        return RGBColor(59, 130, 246)
    try:
        r = int(hex_clean[0:2], 16)
        g = int(hex_clean[2:4], 16)
        b = int(hex_clean[4:6], 16)
        return RGBColor(r, g, b)
    except Exception:
        return RGBColor(59, 130, 246)


def get_image_aspect_ratio(image_path: str) -> float:
    """Return width / height aspect ratio of image."""
    try:
        with Image.open(image_path) as img:
            w, h = img.size
            return float(w) / float(h)
    except Exception:
        return 16.0 / 9.0


class PresentationCompiler:
    def __init__(self, slide_plan: dict, image_catalog: dict = None, logo_config: dict = None):
        """
        slide_plan: Generated JSON plan containing deck_title, theme, slides.
        image_catalog: Dict mapping image_id to local file_path.
        logo_config: {'image_id': str, 'placement': 'top-right' | 'top-left' | 'cover-only'}
        """
        self.plan = slide_plan
        self.image_catalog = image_catalog or {}
        self.logo_config = logo_config or {}

        # Sanitize deck_title so footer never has prompt instruction text
        from identity_engine import is_prompt_instruction
        current_title = self.plan.get("deck_title", "")
        if not current_title or is_prompt_instruction(current_title):
            self.plan["deck_title"] = "Enterprise Strategic Diagnostic"
        
        # Resolve Theme Colors
        theme = self.plan.get("theme", {})
        self.bg_color = hex_to_rgb(theme.get("bg_color", "#FFFFFF"))
        self.text_color = hex_to_rgb(theme.get("text_color", "#0F172A"))
        self.heading_color = hex_to_rgb(theme.get("heading_color") or "#1D4ED8")
        self.subheading_color = hex_to_rgb(theme.get("subheading_color") or "#0284C7")
        self.primary_color = hex_to_rgb(theme.get("primary_color", "#1D4ED8"))
        self.secondary_color = hex_to_rgb(theme.get("secondary_color", "#E2E8F0"))
        self.accent_color = hex_to_rgb(theme.get("accent_color", "#1D4ED8"))
        self.card_bg_color = hex_to_rgb(theme.get("card_bg_color", "#FFFFFF"))
        self.muted_text_color = hex_to_rgb(theme.get("muted_text_color", "#64748B"))
        
        # Primary Font
        self.font_name = "Segoe UI"

        # Initialize Presentation
        self.prs = Presentation()
        self.prs.slide_width = Inches(SLIDE_WIDTH_INCHES)
        self.prs.slide_height = Inches(SLIDE_HEIGHT_INCHES)
        self.blank_layout = self.prs.slide_layouts[6] # Blank slide

    def _set_slide_background(self, slide):
        """Fill slide background with theme background color."""
        bg_shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, 0, 0, Inches(SLIDE_WIDTH_INCHES), Inches(SLIDE_HEIGHT_INCHES)
        )
        bg_shape.fill.solid()
        bg_shape.fill.fore_color.rgb = self.bg_color
        bg_shape.line.fill.background() # No border
        return bg_shape

    def _add_header(self, slide, kicker: str, title: str, subtitle: str = ""):
        """Render modern, clean executive slide header with kicker and title."""
        # Top clean accent line
        accent_bar = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.45), Inches(0.6), Inches(0.04)
        )
        accent_bar.fill.solid()
        accent_bar.fill.fore_color.rgb = self.subheading_color
        accent_bar.line.fill.background()

        # Header text box
        header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.55), Inches(11.0), Inches(1.3))
        tf = header_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        # Kicker paragraph (Light Blue)
        p_kicker = tf.paragraphs[0]
        p_kicker.text = (kicker or "STRATEGIC OVERVIEW").upper()
        p_kicker.font.name = self.font_name
        p_kicker.font.size = Pt(10)
        p_kicker.font.bold = True
        p_kicker.font.color.rgb = self.subheading_color
        p_kicker.space_after = Pt(4)

        # Title paragraph (Blue)
        p_title = tf.add_paragraph()
        p_title.text = title or "Executive Overview"
        p_title.font.name = self.font_name
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = self.heading_color
        p_title.space_after = Pt(4)

        # Subtitle paragraph (Light Blue)
        if subtitle:
            p_sub = tf.add_paragraph()
            p_sub.text = subtitle
            p_sub.font.name = self.font_name
            p_sub.font.size = Pt(13)
            p_sub.font.color.rgb = self.subheading_color

    def _add_footer(self, slide, current_slide: int, total_slides: int):
        """Add subtle slide footer with page number and brand stamp ONLY IF explicitly requested."""
        footer_text = (self.plan.get("footer_text") or "").strip()
        if not footer_text:
            return  # User specified: NO FOOTER unless explicitly instructed

        # Thin divider
        div = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(7.0), Inches(11.733), Inches(0.015)
        )
        div.fill.solid()
        div.fill.fore_color.rgb = self.secondary_color
        div.line.fill.background()

        # Footer text
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(9.5), Inches(0.35))
        tf = footer_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p = tf.paragraphs[0]
        p.text = footer_text
        p.font.name = self.font_name
        p.font.size = Pt(9)
        p.font.color.rgb = self.muted_text_color

        # Slide number on right
        num_box = slide.shapes.add_textbox(Inches(10.5), Inches(7.05), Inches(2.0), Inches(0.35))
        ntf = num_box.text_frame
        np = ntf.paragraphs[0]
        np.alignment = PP_ALIGN.RIGHT
        np.text = f"{current_slide} / {total_slides}"
        np.font.name = self.font_name
        np.font.size = Pt(9)
        np.font.bold = True
        np.font.color.rgb = self.muted_text_color

        # Embed logo if configured for content slides
        logo_id = self.logo_config.get("image_id")
        placement = self.logo_config.get("placement", "top-right")
        if logo_id and logo_id in self.image_catalog and placement != "cover-only":
            logo_path = self.image_catalog[logo_id]
            if os.path.exists(logo_path):
                try:
                    if placement == "top-left":
                        slide.shapes.add_picture(logo_path, Inches(11.5), Inches(0.5), height=Inches(0.55))
                    else: # top-right
                        slide.shapes.add_picture(logo_path, Inches(11.7), Inches(0.5), height=Inches(0.55))
                except Exception:
                    pass

    def _render_title_hero(self, slide, data: dict, current_slide: int, total_slides: int):
        """Render Publication-Grade Executive Boardroom Title / Cover Slide."""
        self._set_slide_background(slide)

        # 1. Left Vertical Grounding Ribbon
        left_ribbon = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.18), Inches(SLIDE_HEIGHT_INCHES)
        )
        left_ribbon.fill.solid()
        left_ribbon.fill.fore_color.rgb = self.primary_color
        left_ribbon.line.fill.background()

        # 2. Top Precision Accent Strip
        top_accent = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0.18), 0, Inches(SLIDE_WIDTH_INCHES - 0.18), Inches(0.06)
        )
        top_accent.fill.solid()
        top_accent.fill.fore_color.rgb = self.subheading_color
        top_accent.line.fill.background()

        # 3. Top Executive Status Pill
        pill_w = Inches(3.6)
        pill_h = Inches(0.38)
        pill_x = Inches(0.9)
        pill_y = Inches(0.85)

        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, pill_x, pill_y, pill_w, pill_h)
        pill.fill.solid()
        pill.fill.fore_color.rgb = self.secondary_color
        pill.line.color.rgb = self.subheading_color
        pill.line.width = Pt(0.8)

        pill_tf = pill.text_frame
        pill_tf.word_wrap = False
        pill_tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        pill_tf.margin_left = Inches(0.15)
        pill_tf.margin_top = Inches(0.02)
        p_kicker = pill_tf.paragraphs[0]
        kicker_text = (data.get("kicker") or "BOARD OF DIRECTORS BRIEFING").upper()
        p_kicker.text = f"●  {kicker_text}"
        p_kicker.font.name = self.font_name
        p_kicker.font.size = Pt(9.5)
        p_kicker.font.bold = True
        p_kicker.font.color.rgb = self.subheading_color

        # 4. Determine Right Column (Hero image vs Executive Briefing Scope Card)
        image_id = data.get("image_id") or self.logo_config.get("image_id")
        has_image = bool(image_id and image_id in self.image_catalog and os.path.exists(self.image_catalog[image_id]))

        # Left Column Headline Block
        headline_w = Inches(6.8)
        headline_box = slide.shapes.add_textbox(Inches(0.9), Inches(1.45), headline_w, Inches(3.9))
        htf = headline_box.text_frame
        htf.word_wrap = True
        htf.margin_left = htf.margin_top = htf.margin_right = htf.margin_bottom = 0

        # Title
        p_title = htf.paragraphs[0]
        p_title.text = data.get("title") or self.plan.get("deck_title", "Executive Strategic Diagnostic")
        p_title.font.name = self.font_name
        p_title.font.size = Pt(32)
        p_title.font.bold = True
        p_title.font.color.rgb = self.heading_color
        p_title.space_after = Pt(14)

        # Subtitle
        p_sub = htf.add_paragraph()
        p_sub.text = data.get("subtitle") or self.plan.get("deck_subtitle", "Comprehensive Quantitative Diagnostics, Data Intelligence, and Strategic Roadmap")
        p_sub.font.name = self.font_name
        p_sub.font.size = Pt(14)
        p_sub.font.color.rgb = self.muted_text_color
        p_sub.space_after = Pt(20)

        # Strategic Badge Tag
        p_tag = htf.add_paragraph()
        p_tag.text = "Target Audience: CXOs & Board of Directors  •  Governance Grade Diagnostic"
        p_tag.font.name = self.font_name
        p_tag.font.size = Pt(10)
        p_tag.font.bold = True
        p_tag.font.color.rgb = self.subheading_color

        # 5. Right Column Panel
        right_x = Inches(8.0)
        right_y = Inches(1.15)
        right_w = Inches(4.5)
        right_h = Inches(4.3)

        if has_image:
            img_path = self.image_catalog[image_id]
            try:
                # Add framed container
                img_frame = slide.shapes.add_shape(
                    MSO_SHAPE.ROUNDED_RECTANGLE, right_x, right_y, right_w, right_h
                )
                img_frame.fill.solid()
                img_frame.fill.fore_color.rgb = self.card_bg_color
                img_frame.line.color.rgb = self.secondary_color
                img_frame.line.width = Pt(1)

                # Exhibit header
                top_strip = slide.shapes.add_shape(
                    MSO_SHAPE.RECTANGLE, right_x, right_y, right_w, Inches(0.08)
                )
                top_strip.fill.solid()
                top_strip.fill.fore_color.rgb = self.subheading_color
                top_strip.line.fill.background()

                aspect = get_image_aspect_ratio(img_path)
                max_w_in = 3.9
                max_h_in = 3.5

                if aspect >= 1.0:
                    w_in = max_w_in
                    h_in = max_w_in / aspect
                else:
                    h_in = max_h_in
                    w_in = max_h_in * aspect

                offset_x = right_x + (right_w - Inches(w_in)) / 2
                offset_y = right_y + Inches(0.3) + (Inches(max_h_in) - Inches(h_in)) / 2
                slide.shapes.add_picture(img_path, offset_x, offset_y, width=Inches(w_in), height=Inches(h_in))
            except Exception as err:
                print(f"Error adding cover picture: {err}")
        else:
            # Executive Briefing Scope Card (Eliminates empty space with high-value analytical structure)
            card = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, right_x, right_y, right_w, right_h
            )
            card.fill.solid()
            card.fill.fore_color.rgb = self.card_bg_color
            card.line.color.rgb = self.secondary_color
            card.line.width = Pt(1.2)

            # Top Accent Line
            top_line = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, right_x, right_y, right_w, Inches(0.08)
            )
            top_line.fill.solid()
            top_line.fill.fore_color.rgb = self.subheading_color
            top_line.line.fill.background()

            # Text inside Briefing Scope Card
            card_tb = slide.shapes.add_textbox(
                right_x + Inches(0.3), right_y + Inches(0.25), right_w - Inches(0.6), right_h - Inches(0.5)
            )
            ctf = card_tb.text_frame
            ctf.word_wrap = True
            ctf.margin_left = ctf.margin_top = ctf.margin_right = ctf.margin_bottom = 0

            # Card Header
            cp0 = ctf.paragraphs[0]
            cp0.text = "EXECUTIVE BRIEFING SCOPE"
            cp0.font.name = self.font_name
            cp0.font.size = Pt(11)
            cp0.font.bold = True
            cp0.font.color.rgb = self.heading_color
            cp0.space_after = Pt(4)

            # Sub-label
            cp_sub = ctf.add_paragraph()
            cp_sub.text = "Strategic agenda & diagnostic dimensions:"
            cp_sub.font.name = self.font_name
            cp_sub.font.size = Pt(9.5)
            cp_sub.font.color.rgb = self.muted_text_color
            cp_sub.space_after = Pt(14)

            # Focus pillars (from focus_areas or default)
            focus_items = data.get("focus_areas") or [
                "Empirical Diagnostics: Quantitative evaluation across core operational dimensions",
                "Divisional Parity Analysis: Benchmarking high-performer compensation and capacity",
                "Workforce Capacity Dynamics: SOP FTE to EOP retention trajectories",
                "Strategic Governance Roadmap: Boardroom resolutions and priority next steps"
            ]

            for item in focus_items[:4]:
                p_item = ctf.add_paragraph()
                p_item.text = f"▪  {item}"
                p_item.font.name = self.font_name
                p_item.font.size = Pt(9.5)
                p_item.font.color.rgb = self.text_color
                p_item.space_after = Pt(10)

        # 6. Bottom Boardroom Metadata Ribbon (4 Columns)
        div_y = Inches(5.8)
        divider = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0.9), div_y, Inches(11.6), Inches(0.015)
        )
        divider.fill.solid()
        divider.fill.fore_color.rgb = self.secondary_color
        divider.line.fill.background()

        meta_y = div_y + Inches(0.15)
        presenter = data.get("presenter") or "Executive Advisory • Strategic Intelligence"

        meta_cols = [
            ("PREPARED FOR", "Board of Directors / CXO Leadership", Inches(0.9), Inches(3.0)),
            ("PREPARED BY", presenter, Inches(4.1), Inches(3.0)),
            ("DATE & CYCLE", "Annual Strategy & Compensation Review", Inches(7.3), Inches(2.5)),
            ("CLASSIFICATION", "STRICTLY CONFIDENTIAL", Inches(10.0), Inches(2.5))
        ]

        for label, val, col_x, col_w in meta_cols:
            m_box = slide.shapes.add_textbox(col_x, meta_y, col_w, Inches(0.9))
            mtf = m_box.text_frame
            mtf.word_wrap = True
            mtf.margin_left = mtf.margin_top = mtf.margin_right = mtf.margin_bottom = 0

            mp_lbl = mtf.paragraphs[0]
            mp_lbl.text = label
            mp_lbl.font.name = self.font_name
            mp_lbl.font.size = Pt(8)
            mp_lbl.font.bold = True
            mp_lbl.font.color.rgb = self.muted_text_color
            mp_lbl.space_after = Pt(2)

            mp_val = mtf.add_paragraph()
            mp_val.text = val
            mp_val.font.name = self.font_name
            mp_val.font.size = Pt(10)
            mp_val.font.bold = True
            mp_val.font.color.rgb = self.heading_color if label == "CLASSIFICATION" else self.text_color

    def _render_stats_kpis(self, slide, data: dict, current_slide: int, total_slides: int):
        """Render High-Impact KPI / Quantitative Metrics Slide."""
        self._set_slide_background(slide)
        self._add_header(slide, data.get("kicker"), data.get("title"), data.get("subtitle"))

        stats = data.get("stats", [])
        if not stats:
            stats = [
                {"value": "$4.8M", "label": "Annual Recurring Revenue", "change": "+280% YoY"},
                {"value": "142+", "label": "Enterprise Customers", "change": "98% NDR"},
                {"value": "84%", "label": "Gross Margin", "change": "Top Quartile"}
            ]

        num_cards = min(len(stats), 4)
        total_width = Inches(11.733)
        gap = Inches(0.3)
        card_w = (total_width - (gap * (num_cards - 1))) / num_cards
        card_h = Inches(4.5)
        top_y = Inches(2.1)

        for i in range(num_cards):
            left_x = Inches(0.8) + i * (card_w + gap)
            st = stats[i]

            # Card Container
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_x, top_y, card_w, card_h)
            card.fill.solid()
            card.fill.fore_color.rgb = self.card_bg_color
            card.line.color.rgb = self.secondary_color
            card.line.width = Pt(1)

            # Top Accent Stripe on each card
            top_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left_x, top_y, card_w, Inches(0.08))
            top_line.fill.solid()
            top_line.fill.fore_color.rgb = self.subheading_color
            top_line.line.fill.background()

            # Content inside card
            tbox = slide.shapes.add_textbox(left_x + Inches(0.25), top_y + Inches(0.4), card_w - Inches(0.5), card_h - Inches(0.6))
            tf = tbox.text_frame
            tf.word_wrap = True

            # Value (Massive metric text in Blue)
            p_val = tf.paragraphs[0]
            p_val.text = str(st.get("value", "0"))
            p_val.font.name = self.font_name
            p_val.font.size = Pt(40)
            p_val.font.bold = True
            p_val.font.color.rgb = self.heading_color
            p_val.space_after = Pt(8)

            # Change / Delta Pill
            change = st.get("change") or st.get("growth")
            if change:
                p_chg = tf.add_paragraph()
                p_chg.text = f"▲  {change}"
                p_chg.font.name = self.font_name
                p_chg.font.size = Pt(13)
                p_chg.font.bold = True
                p_chg.font.color.rgb = RGBColor(16, 185, 129) # Emerald Green highlight
                p_chg.space_after = Pt(14)

            # Label / Description
            p_lbl = tf.add_paragraph()
            p_lbl.text = str(st.get("label", "Metric Title"))
            p_lbl.font.name = self.font_name
            p_lbl.font.size = Pt(15)
            p_lbl.font.bold = True
            p_lbl.font.color.rgb = self.text_color
            p_lbl.space_after = Pt(8)

            # Subtext if present
            subtext = st.get("subtext") or st.get("description")
            if subtext:
                p_desc = tf.add_paragraph()
                p_desc.text = str(subtext)
                p_desc.font.name = self.font_name
                p_desc.font.size = Pt(12)
                p_desc.font.color.rgb = self.muted_text_color

        self._add_footer(slide, current_slide, total_slides)

    def _render_cards_grid(self, slide, data: dict, current_slide: int, total_slides: int):
        """Render Modern 3 or 4 Column Cards Layout."""
        self._set_slide_background(slide)
        self._add_header(slide, data.get("kicker"), data.get("title"), data.get("subtitle"))

        cards = data.get("cards", [])
        if not cards:
            cards = [
                {"badge": "01", "title": "Core Initiative", "description": "Key strategic driver delivering customer value."},
                {"badge": "02", "title": "Scalable Model", "description": "High gross margin economics with built-in network effects."},
                {"badge": "03", "title": "Market Defense", "description": "Deep technological moats and enterprise compliance lock-in."}
            ]

        num_cards = min(len(cards), 4)
        total_width = Inches(11.733)
        gap = Inches(0.3)
        card_w = (total_width - (gap * (num_cards - 1))) / num_cards
        card_h = Inches(4.5)
        top_y = Inches(2.1)

        for i in range(num_cards):
            left_x = Inches(0.8) + i * (card_w + gap)
            cd = cards[i]

            # Card shape
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_x, top_y, card_w, card_h)
            card.fill.solid()
            card.fill.fore_color.rgb = self.card_bg_color
            card.line.color.rgb = self.secondary_color
            card.line.width = Pt(1)

            # Card text content
            tbox = slide.shapes.add_textbox(left_x + Inches(0.3), top_y + Inches(0.35), card_w - Inches(0.6), card_h - Inches(0.7))
            tf = tbox.text_frame
            tf.word_wrap = True

            # Badge pill
            p_badge = tf.paragraphs[0]
            badge_val = cd.get("badge") or f"0{i+1}"
            p_badge.text = f"[ {badge_val} ]"
            p_badge.font.name = self.font_name
            p_badge.font.size = Pt(12)
            p_badge.font.bold = True
            p_badge.font.color.rgb = self.subheading_color
            p_badge.space_after = Pt(12)

            # Card Title (Blue)
            p_title = tf.add_paragraph()
            p_title.text = str(cd.get("title", f"Pillar {i+1}"))
            p_title.font.name = self.font_name
            p_title.font.size = Pt(18)
            p_title.font.bold = True
            p_title.font.color.rgb = self.heading_color
            p_title.space_after = Pt(12)

            # Card Description
            p_desc = tf.add_paragraph()
            p_desc.text = str(cd.get("description", ""))
            p_desc.font.name = self.font_name
            p_desc.font.size = Pt(13)
            p_desc.font.color.rgb = self.muted_text_color

        self._add_footer(slide, current_slide, total_slides)

    def _render_split_image_text(self, slide, data: dict, current_slide: int, total_slides: int):
        """Render 50/50 Split Screen: Narrative/Bullets on Left, Image on Right."""
        self._set_slide_background(slide)
        self._add_header(slide, data.get("kicker"), data.get("title"), data.get("subtitle"))

        left_w = Inches(5.8)
        right_w = Inches(5.6)
        top_y = Inches(2.1)
        content_h = Inches(4.5)

        # Left Column: Points / Narrative container
        bullets = data.get("bullets", [])
        if not bullets and "cards" in data:
            bullets = [f"{c.get('title')}: {c.get('description')}" for c in data["cards"]]
        if not bullets:
            bullets = [
                "Continuous automated synchronization with core business data stores",
                "High availability architecture with fault-tolerant distributed nodes",
                "Demonstrated ROI across benchmark enterprise pilot deployments"
            ]

        # Container card for bullets
        left_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top_y, left_w, content_h)
        left_card.fill.solid()
        left_card.fill.fore_color.rgb = self.card_bg_color
        left_card.line.color.rgb = self.secondary_color
        left_card.line.width = Pt(1)

        tbox = slide.shapes.add_textbox(Inches(1.1), top_y + Inches(0.4), left_w - Inches(0.6), content_h - Inches(0.8))
        tf = tbox.text_frame
        tf.word_wrap = True

        p_init = tf.paragraphs[0]
        p_init.text = "KEY TAKEAWAYS & EVIDENCE"
        p_init.font.name = self.font_name
        p_init.font.size = Pt(11)
        p_init.font.bold = True
        p_init.font.color.rgb = self.accent_color
        p_init.space_after = Pt(16)

        for b in bullets:
            p_b = tf.add_paragraph()
            p_b.text = f"▪   {b}"
            p_b.font.name = self.font_name
            p_b.font.size = Pt(13)
            p_b.font.color.rgb = self.text_color
            p_b.space_after = Pt(14)

        # Right Column: User Image or Visual Graphic
        right_x = Inches(6.933)
        img_id = data.get("image_id")
        has_image = bool(img_id and img_id in self.image_catalog and os.path.exists(self.image_catalog[img_id]))

        # Container frame
        right_frame = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_x, top_y, right_w, content_h)
        right_frame.fill.solid()
        right_frame.fill.fore_color.rgb = self.card_bg_color
        right_frame.line.color.rgb = self.secondary_color
        right_frame.line.width = Pt(1)

        if has_image:
            img_path = self.image_catalog[img_id]
            try:
                aspect = get_image_aspect_ratio(img_path)
                avail_w_in = 5.6 - 0.6  # 5.0 inches
                avail_h_in = 4.5 - 0.6  # 3.9 inches

                if (avail_w_in / avail_h_in) > aspect:
                    h_in = avail_h_in
                    w_in = h_in * aspect
                else:
                    w_in = avail_w_in
                    h_in = w_in / aspect

                x_off = right_x + Inches((5.6 - w_in) / 2)
                y_off = top_y + Inches((4.5 - h_in) / 2)
                slide.shapes.add_picture(img_path, x_off, y_off, width=Inches(w_in), height=Inches(h_in))
            except Exception as err:
                print(f"Error adding picture to split slide: {err}")
                has_image = False

        if not has_image:
            # Fallback visual graphic
            rt_box = slide.shapes.add_textbox(right_x + Inches(0.5), top_y + Inches(1.2), right_w - Inches(1.0), Inches(2.0))
            rtf = rt_box.text_frame
            rtf.word_wrap = True
            rp = rtf.paragraphs[0]
            rp.alignment = PP_ALIGN.CENTER
            rp.text = "STRATEGIC IMPACT"
            rp.font.name = self.font_name
            rp.font.size = Pt(18)
            rp.font.bold = True
            rp.font.color.rgb = self.accent_color
            rp.space_after = Pt(12)

            rp2 = rtf.add_paragraph()
            rp2.alignment = PP_ALIGN.CENTER
            rp2.text = "Data-driven execution across modern enterprise operational benchmarks."
            rp2.font.name = self.font_name
            rp2.font.size = Pt(13)
            rp2.font.color.rgb = self.muted_text_color

        self._add_footer(slide, current_slide, total_slides)

    def _render_chart_focus(self, slide, data: dict, current_slide: int, total_slides: int):
        """Render Dedicated Chart Deep-Dive Slide: 60% Width Chart + Strategic Insights."""
        self._set_slide_background(slide)
        self._add_header(
            slide,
            data.get("kicker") or "EXECUTIVE DATA INTELLIGENCE",
            data.get("title") or "Workforce Analytics & Strategic Distribution",
            data.get("subtitle") or "Quantitative evaluation of talent allocation and compensation equity"
        )

        top_y = Inches(2.05)
        content_h = Inches(4.65)
        left_w = Inches(4.6)
        right_w = Inches(6.833)
        right_x = Inches(5.7)

        # Left Column: Strategic Takeaways & Analysis Card
        left_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top_y, left_w, content_h)
        left_card.fill.solid()
        left_card.fill.fore_color.rgb = self.card_bg_color
        left_card.line.color.rgb = self.secondary_color
        left_card.line.width = Pt(1)

        # Top Accent Stripe on Left Card
        top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), top_y, left_w, Inches(0.08))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = self.subheading_color
        top_bar.line.fill.background()

        tbox = slide.shapes.add_textbox(Inches(1.05), top_y + Inches(0.35), left_w - Inches(0.5), content_h - Inches(0.6))
        tf = tbox.text_frame
        tf.word_wrap = True

        p_kicker = tf.paragraphs[0]
        p_kicker.text = "STRATEGIC TAKEAWAYS"
        p_kicker.font.name = self.font_name
        p_kicker.font.size = Pt(11)
        p_kicker.font.bold = True
        p_kicker.font.color.rgb = self.subheading_color
        p_kicker.space_after = Pt(14)

        bullets = data.get("bullets", [])
        if not bullets and "cards" in data:
            bullets = [f"{c.get('title')}: {c.get('description')}" for c in data["cards"]]
        if not bullets:
            bullets = [
                "Statistically significant variance across operational and corporate business units",
                "Compensation parity demonstrated in high-growth renewable energy initiatives",
                "Talent pipeline concentration highlights immediate executive succession imperatives"
            ]

        for b in bullets:
            p_b = tf.add_paragraph()
            p_b.text = f"▪   {b}"
            p_b.font.name = self.font_name
            p_b.font.size = Pt(12)
            p_b.font.color.rgb = self.text_color
            p_b.space_after = Pt(12)

        # Right Column: Prominent Chart Container Frame
        chart_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_x, top_y, right_w, content_h)
        chart_card.fill.solid()
        chart_card.fill.fore_color.rgb = self.card_bg_color
        chart_card.line.color.rgb = self.secondary_color
        chart_card.line.width = Pt(1)

        # Check for image
        img_id = data.get("image_id")
        has_image = bool(img_id and img_id in self.image_catalog and os.path.exists(self.image_catalog[img_id]))

        if has_image:
            img_path = self.image_catalog[img_id]
            try:
                aspect = get_image_aspect_ratio(img_path)
                # Compute in pure float inches to avoid double-unit EMU multiplication
                avail_w_in = 6.833 - 0.6  # ~6.233 inches
                avail_h_in = 4.65 - 0.7   # ~3.95 inches

                if (avail_w_in / avail_h_in) > aspect:
                    h_in = avail_h_in
                    w_in = h_in * aspect
                else:
                    w_in = avail_w_in
                    h_in = w_in / aspect

                x_off = right_x + Inches((6.833 - w_in) / 2)
                y_off = top_y + Inches((4.65 - h_in) / 2)
                slide.shapes.add_picture(img_path, x_off, y_off, width=Inches(w_in), height=Inches(h_in))
            except Exception as err:
                print(f"Error adding picture to chart slide: {err}")
                has_image = False

        if not has_image:
            # Fallback graphic
            ftbox = slide.shapes.add_textbox(right_x + Inches(0.5), top_y + Inches(1.5), right_w - Inches(1.0), Inches(2.0))
            ftf = ftbox.text_frame
            ftf.word_wrap = True
            fp = ftf.paragraphs[0]
            fp.alignment = PP_ALIGN.CENTER
            fp.text = "EXECUTIVE WORKFORCE ANALYTICS"
            fp.font.name = self.font_name
            fp.font.size = Pt(16)
            fp.font.bold = True
            fp.font.color.rgb = self.accent_color

        # Footnote inside chart card
        fnote = slide.shapes.add_textbox(right_x + Inches(0.3), top_y + content_h - Inches(0.4), right_w - Inches(0.6), Inches(0.3))
        fn_tf = fnote.text_frame
        fn_p = fn_tf.paragraphs[0]
        fn_p.text = "Source: Enterprise HRIS & Talent Analytics • Board of Directors Meeting"
        fn_p.font.name = self.font_name
        fn_p.font.size = Pt(8)
        fn_p.font.color.rgb = self.muted_text_color

        self._add_footer(slide, current_slide, total_slides)

    def _render_timeline_process(self, slide, data: dict, current_slide: int, total_slides: int):
        """Render Process Timeline / Milestone Roadmap Slide."""
        self._set_slide_background(slide)
        self._add_header(slide, data.get("kicker"), data.get("title"), data.get("subtitle"))

        steps = data.get("timeline_steps", [])
        if not steps and "milestones" in data:
            steps = data["milestones"]
        if not steps:
            steps = [
                {"step": "Phase 1", "title": "Architecture & Beta", "description": "Deployment across initial enterprise tier."},
                {"step": "Phase 2", "title": "Commercial Scaling", "description": "Expansion of direct go-to-market channels."},
                {"step": "Phase 3", "title": "Global Ecosystem", "description": "Full multi-region compliance and ecosystem lock."}
            ]

        num_steps = min(len(steps), 4)
        total_width = Inches(11.733)
        gap = Inches(0.3)
        step_w = (total_width - (gap * (num_steps - 1))) / num_steps
        top_y = Inches(2.3)
        card_h = Inches(4.3)

        # Connecting progress line behind steps
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(2.7), Inches(10.9), Inches(0.04))
        line.fill.solid()
        line.fill.fore_color.rgb = self.secondary_color
        line.line.fill.background()

        for i in range(num_steps):
            left_x = Inches(0.8) + i * (step_w + gap)
            st = steps[i]

            # Step Card
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_x, top_y, step_w, card_h)
            card.fill.solid()
            card.fill.fore_color.rgb = self.card_bg_color
            card.line.color.rgb = self.secondary_color
            card.line.width = Pt(1)

            # Step Number Badge Circle/Square
            badge = slide.shapes.add_shape(MSO_SHAPE.OVAL, left_x + Inches(0.3), top_y + Inches(0.3), Inches(0.7), Inches(0.7))
            badge.fill.solid()
            badge.fill.fore_color.rgb = self.accent_color
            badge.line.fill.background()
            
            btf = badge.text_frame
            bp = btf.paragraphs[0]
            bp.alignment = PP_ALIGN.CENTER
            bp.text = str(i+1)
            bp.font.name = self.font_name
            bp.font.size = Pt(14)
            bp.font.bold = True
            bp.font.color.rgb = RGBColor(255, 255, 255)

            # Step Text Container
            tbox = slide.shapes.add_textbox(left_x + Inches(0.3), top_y + Inches(1.2), step_w - Inches(0.6), card_h - Inches(1.4))
            tf = tbox.text_frame
            tf.word_wrap = True

            # Phase label
            phase_label = st.get("step") or st.get("quarter") or f"Stage 0{i+1}"
            p_phase = tf.paragraphs[0]
            p_phase.text = phase_label.upper()
            p_phase.font.name = self.font_name
            p_phase.font.size = Pt(11)
            p_phase.font.bold = True
            p_phase.font.color.rgb = self.subheading_color
            p_phase.space_after = Pt(6)

            # Title (Blue)
            p_title = tf.add_paragraph()
            p_title.text = st.get("title", f"Milestone {i+1}")
            p_title.font.name = self.font_name
            p_title.font.size = Pt(16)
            p_title.font.bold = True
            p_title.font.color.rgb = self.heading_color
            p_title.space_after = Pt(10)

            # Description / Detail
            p_desc = tf.add_paragraph()
            desc = st.get("description") or st.get("detail", "")
            p_desc.text = desc
            p_desc.font.name = self.font_name
            p_desc.font.size = Pt(12)
            p_desc.font.color.rgb = self.muted_text_color

        self._add_footer(slide, current_slide, total_slides)

    def _render_closing_contact(self, slide, data: dict, current_slide: int, total_slides: int):
        """Render Closing / Board Resolutions / Action Plan Slide with balanced dual cards."""
        self._set_slide_background(slide)
        self._add_header(
            slide,
            data.get("kicker") or "CONCLUSION & BOARD ACTION PLAN",
            data.get("title") or "Recommended Resolutions & Executive Next Steps",
            data.get("subtitle") or "Immediate Governance Decisions, Operational Workstreams & Phased Milestones"
        )

        top_y = Inches(2.05)
        content_h = Inches(4.7)
        left_w = Inches(6.6)
        right_w = Inches(4.833)
        right_x = Inches(7.7)

        # -----------------------------------------------------------------
        # LEFT CARD: Immediate Board Resolutions & Action Plan
        # -----------------------------------------------------------------
        left_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), top_y, left_w, content_h)
        left_card.fill.solid()
        left_card.fill.fore_color.rgb = self.card_bg_color
        left_card.line.color.rgb = self.secondary_color
        left_card.line.width = Pt(1)

        # Top Accent Stripe
        l_stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), top_y, left_w, Inches(0.08))
        l_stripe.fill.solid()
        l_stripe.fill.fore_color.rgb = self.heading_color
        l_stripe.line.fill.background()

        tbox = slide.shapes.add_textbox(Inches(1.1), top_y + Inches(0.3), left_w - Inches(0.6), content_h - Inches(0.5))
        tf = tbox.text_frame
        tf.word_wrap = True

        p_k = tf.paragraphs[0]
        p_k.text = "●  PRIORITY EXECUTIVE WORKSTREAMS"
        p_k.font.name = self.font_name
        p_k.font.size = Pt(10)
        p_k.font.bold = True
        p_k.font.color.rgb = self.subheading_color
        p_k.space_after = Pt(8)

        p_t = tf.add_paragraph()
        p_t.text = "Immediate Board Resolutions"
        p_t.font.name = self.font_name
        p_t.font.size = Pt(18)
        p_t.font.bold = True
        p_t.font.color.rgb = self.heading_color
        p_t.space_after = Pt(14)

        bullets = data.get("bullets", [])
        if not bullets and "cards" in data:
            bullets = [f"{c.get('title')}: {c.get('description')}" for c in data["cards"]]
        if not bullets:
            bullets = [
                "Charter cross-divisional compensation taskforce to institutionalize parity across technical divisions",
                "Approve targeted leadership development pathways for emerging operational talent",
                "Mandate quarterly demographic & compensation audits presented directly to Board Governance Committee",
                "Authorize phased 90-day technical resource allocation roadmap with audited milestone sign-offs"
            ]

        for b in bullets[:5]:
            p_b = tf.add_paragraph()
            p_b.text = f"✔   {b}"
            p_b.font.name = self.font_name
            p_b.font.size = Pt(11)
            p_b.font.color.rgb = self.text_color
            p_b.space_after = Pt(10)

        # -----------------------------------------------------------------
        # RIGHT CARD: Governance, Cadence & Direct Advisory Contact
        # -----------------------------------------------------------------
        right_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right_x, top_y, right_w, content_h)
        right_card.fill.solid()
        right_card.fill.fore_color.rgb = self.card_bg_color
        right_card.line.color.rgb = self.secondary_color
        right_card.line.width = Pt(1)

        # Top Accent Stripe
        r_stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, right_x, top_y, right_w, Inches(0.08))
        r_stripe.fill.solid()
        r_stripe.fill.fore_color.rgb = self.subheading_color
        r_stripe.line.fill.background()

        rtbox = slide.shapes.add_textbox(right_x + Inches(0.3), top_y + Inches(0.3), right_w - Inches(0.6), content_h - Inches(0.5))
        rtf = rtbox.text_frame
        rtf.word_wrap = True

        rp_k = rtf.paragraphs[0]
        rp_k.text = "●  GOVERNANCE & EXECUTION"
        rp_k.font.name = self.font_name
        rp_k.font.size = Pt(10)
        rp_k.font.bold = True
        rp_k.font.color.rgb = self.subheading_color
        rp_k.space_after = Pt(8)

        rp_t = rtf.add_paragraph()
        rp_t.text = "Steering & Advisory Cadence"
        rp_t.font.name = self.font_name
        rp_t.font.size = Pt(18)
        rp_t.font.bold = True
        rp_t.font.color.rgb = self.heading_color
        rp_t.space_after = Pt(14)

        gov_items = [
            ("Steering Cadence", "Bi-weekly executive reviews with leadership committee"),
            ("Board Oversight", "Quarterly milestone audit with Board Governance Committee"),
            ("Target Horizon", "90-Day phased execution window with quantitative sign-offs"),
            ("Advisory Contact", "Senior Practice Leadership • strategic-advisory@company.com")
        ]

        for label, desc in gov_items:
            p_lbl = rtf.add_paragraph()
            p_lbl.text = f"▪  {label.upper()}"
            p_lbl.font.name = self.font_name
            p_lbl.font.size = Pt(10)
            p_lbl.font.bold = True
            p_lbl.font.color.rgb = self.subheading_color
            p_lbl.space_after = Pt(2)

            p_val = rtf.add_paragraph()
            p_val.text = desc
            p_val.font.name = self.font_name
            p_val.font.size = Pt(11)
            p_val.font.color.rgb = self.muted_text_color
            p_val.space_after = Pt(8)

        self._add_footer(slide, current_slide, total_slides)

    def compile(self, output_path: str) -> str:
        """Compile presentation from slide plan and save to output_path."""
        slides_data = self.plan.get("slides", [])
        total = len(slides_data)

        for idx, slide_item in enumerate(slides_data, start=1):
            slide = self.prs.slides.add_slide(self.blank_layout)
            layout_type = slide_item.get("layout_type", "cards_grid")

            if layout_type == "title_hero" or idx == 1:
                self._render_title_hero(slide, slide_item, idx, total)
            elif layout_type == "stats_kpis":
                self._render_stats_kpis(slide, slide_item, idx, total)
            elif layout_type == "cards_grid":
                self._render_cards_grid(slide, slide_item, idx, total)
            elif layout_type == "chart_focus":
                self._render_chart_focus(slide, slide_item, idx, total)
            elif layout_type == "split_image_text":
                self._render_split_image_text(slide, slide_item, idx, total)
            elif layout_type == "timeline_process":
                self._render_timeline_process(slide, slide_item, idx, total)
            elif layout_type == "closing_contact":
                self._render_closing_contact(slide, slide_item, idx, total)
            else:
                # Default fallback to cards grid
                self._render_cards_grid(slide, slide_item, idx, total)

            # Inject Speaker Notes into native PowerPoint notes pane
            notes = slide_item.get("notes")
            if notes:
                try:
                    notes_slide = slide.notes_slide
                    tf_notes = notes_slide.notes_text_frame
                    tf_notes.text = str(notes).strip()
                except Exception:
                    pass

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.prs.save(output_path)
        return output_path
