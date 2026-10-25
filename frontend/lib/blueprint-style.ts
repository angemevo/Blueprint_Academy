/** Couleurs du canvas, inspirées des conventions de l'éditeur Blueprint. */

export const PIN_COLORS: Record<string, string> = {
  exec: "#ffffff",
  bool: "#940000",
  int: "#1fe0a8",
  float: "#9cfc4b",
  string: "#f700c8",
  name: "#c477ff",
  object: "#00a2ff",
  struct: "#0058c6",
  wildcard: "#808080",
};

export const NEUTRAL_PIN_COLOR = "#808080";

export const CATEGORY_COLORS: Record<string, string> = {
  events: "#a31515",
  flow_control: "#6b6b6b",
  variables: "#2f7d6d",
  functions: "#2a5fa8",
  math: "#2f8f4e",
  actors: "#2a7fa8",
  components: "#1f7a99",
  ui: "#8a5a1f",
  audio_fx: "#7a3f9a",
  utility: "#4a5568",
};

export const NEUTRAL_HEADER_COLOR = "#3a3f4b";

export const pinColor = (type: string | undefined) =>
  (type && PIN_COLORS[type]) || NEUTRAL_PIN_COLOR;
