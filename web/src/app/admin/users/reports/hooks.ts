import { useState } from "react";
import useSWR, { mutate } from "swr";
import { buildApiPath } from "@/lib/urlBuilder";
import { ChatSessionGroupResponse, GroupingType } from "./types";
import {
  convertDateToStartOfDay,
  convertDateToEndOfDay,
  getXDaysAgo,
} from "./dateUtils";
import { DateRangePickerValue, THIRTY_DAYS } from "./DateRangeSelector";

export const useTimeRange = () => {
  return useState<DateRangePickerValue>({
    to: new Date(),
    from: getXDaysAgo(30),
    selectValue: THIRTY_DAYS,
  });
};

export const useChatSessionGroups = (
  timeRange: DateRangePickerValue,
  groupingType: GroupingType
) => {
  const url = buildApiPath("/api/admin/chat-session-groups");

  const { data, error, isLoading } = useSWR<ChatSessionGroupResponse>(
    timeRange?.from && timeRange?.to
      ? [
          url,
          {
            start_time: convertDateToStartOfDay(timeRange.from)?.toISOString(),
            end_time: convertDateToEndOfDay(timeRange.to)?.toISOString(),
            grouping_type: groupingType,
          },
        ]
      : null,
    async ([url, payload]) => {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        throw new Error("Failed to fetch chat session groups");
      }
      return response.json();
    }
  );

  return {
    data,
    error,
    isLoading,
    refreshChatSessionGroups: () => mutate(url),
  };
};
