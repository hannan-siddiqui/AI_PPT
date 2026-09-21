export interface ThemeConfig {
  name: string;
  primary_color: string;
  secondary_color: string;
  accent_color: string;
  bg_color: string;
  text_color: string;
  card_bg_color: string;
  muted_text_color?: string;
  heading_color?: string;
  subheading_color?: string;
}

export interface UploadedImage {
  id: string;
  filename: string;
  original_name: string;
  url: string;
  width: number;
  height: number;
  role: 'logo' | 'hero' | 'chart' | 'team' | 'graphic';
  path?: string;
  file?: File;
}

export interface StatItem {
  value: string;
  label: string;
  change?: string;
  subtext?: string;
}

export interface CardItem {
  badge?: string;
  title: string;
  description: string;
}

export interface TimelineItem {
  step?: string;
  quarter?: string;
  title: string;
  description?: string;
  detail?: string;
}

export interface SlideData {
  slide_number: number;
  layout_type: 'title_hero' | 'stats_kpis' | 'cards_grid' | 'split_image_text' | 'chart_focus' | 'timeline_process' | 'closing_contact' | string;
  kicker?: string;
  title: string;
  subtitle?: string;
  presenter?: string;
  bullets?: string[];
  stats?: StatItem[];
  cards?: CardItem[];
  timeline_steps?: TimelineItem[];
  focus_areas?: string[];
  image_id?: string | null;
  image_url?: string | null;
  notes?: string;
}

export interface SlidePlan {
  deck_title: string;
  deck_subtitle?: string;
  footer_text?: string | null;
  theme: ThemeConfig;
  slides: SlideData[];
}

export interface QAJudgeReport {
  passed: boolean;
  score: number;
  feedback: string;
  clipping_risk_detected: boolean;
  checked_slides_count: number;
  suggested_adjustments: string[];
  applied_fixes: string[];
}

export interface GeneratePptResponse {
  success: boolean;
  deck_id: string;
  filename: string;
  download_url: string;
  slide_count: number;
  plan: SlidePlan;
  images?: UploadedImage[];
  qa_report?: QAJudgeReport;
  logs?: string[];
  error?: string;
}

export interface JobStatusResponse {
  job_id: string;
  status: 'queued' | 'ingesting' | 'analyzing_images' | 'reasoning_and_planning' | 'assembling_slides' | 'vlm_judge' | 'completed' | 'failed';
  step: string;
  progress: number;
  logs?: string[];
  result?: GeneratePptResponse;
  error?: string;
}
