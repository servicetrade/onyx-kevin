export type GroupingType = "user" | "assistant";

export interface ChatSessionGroupData {
  name: string;
  count: number;
}

export interface ChatSessionGroupResponse {
  data: ChatSessionGroupData[];
  total_rows: number;
  total_sessions: number;
}

export interface ChartData {
  name: string;
  value: number;
}
