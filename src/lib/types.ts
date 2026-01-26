export interface Font {
  name: string;
  desc: string;
  category: string;
}

export interface ChatMessage {
  role: "user" | "model";
  text: string;
}

export interface SearchResponse {
  reply: string;
  fonts: Font[];
}
