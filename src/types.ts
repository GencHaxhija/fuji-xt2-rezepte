export interface Recipe {
  id?: string;
  name: string;
  kategorie: string;
  film_simulation: string;
  weissabgleich: string;
  wb_shift: string;
  dynamikbereich: string;
  lichter: number;
  schatten: number;
  farbe: number;
  schaerfe: number;
  rauschreduzierung: number;
  grain: string;
  tone_curve: string;
  color_chrome: string;
  bild_url: string;
  tags: string;
  notizen: string;
  quelle: string;
  favorit: boolean;
  datum: string;
}
