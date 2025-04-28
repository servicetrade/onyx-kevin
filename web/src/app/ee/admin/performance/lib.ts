import { errorHandlingFetcher } from "@/lib/fetcher";
import useSWR, { mutate } from "swr";
import {
  ChatSessionGroupResponse,
  GroupingType,
  OnyxBotAnalytics,
  QueryAnalytics,
  UserAnalytics,
} from "./usage/types";
import { useState } from "react";
import { buildApiPath } from "@/lib/urlBuilder";

import {
  convertDateToEndOfDay,
  convertDateToStartOfDay,
  getXDaysAgo,
} from "./dateUtils";
import { THIRTY_DAYS } from "./DateRangeSelector";
import { DateRangePickerValue } from "@/app/ee/admin/performance/DateRangeSelector";

export const useTimeRange = () => {
  return useState<DateRangePickerValue>({
    to: new Date(),
    from: getXDaysAgo(30),
    selectValue: THIRTY_DAYS,
  });
};

export const useQueryAnalytics = (timeRange: DateRangePickerValue) => {
  const url = buildApiPath("/api/analytics/admin/query", {
    start: convertDateToStartOfDay(timeRange.from)?.toISOString(),
    end: convertDateToEndOfDay(timeRange.to)?.toISOString(),
  });
  const swrResponse = useSWR<QueryAnalytics[]>(url, errorHandlingFetcher);

  return {
    ...swrResponse,
    refreshQueryAnalytics: () => mutate(url),
  };
};

export const useUserAnalytics = (timeRange: DateRangePickerValue) => {
  const url = buildApiPath("/api/analytics/admin/user", {
    start: convertDateToStartOfDay(timeRange.from)?.toISOString(),
    end: convertDateToEndOfDay(timeRange.to)?.toISOString(),
  });
  const swrResponse = useSWR<UserAnalytics[]>(url, errorHandlingFetcher);

  return {
    ...swrResponse,
    refreshUserAnalytics: () => mutate(url),
  };
};

export const useOnyxBotAnalytics = (timeRange: DateRangePickerValue) => {
  const url = buildApiPath("/api/analytics/admin/onyxbot", {
    start: convertDateToStartOfDay(timeRange.from)?.toISOString(),
    end: convertDateToEndOfDay(timeRange.to)?.toISOString(),
  });
  const swrResponse = useSWR<OnyxBotAnalytics[]>(url, errorHandlingFetcher); // TODO

  return {
    ...swrResponse,
    refreshOnyxBotAnalytics: () => mutate(url),
  };
};

export function getDatesList(startDate: Date): string[] {
  const datesList: string[] = [];
  const endDate = new Date(); // current date

  for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
    const dateStr = d.toISOString().split("T")[0]; // convert date object to 'YYYY-MM-DD' format
    datesList.push(dateStr);
  }

  return datesList;
}

export interface PersonaMessageAnalytics {
  total_messages: number;
  date: string;
  persona_id: number;
}

export interface PersonaSnapshot {
  id: number;
  name: string;
  description: string;
  is_visible: boolean;
  is_public: boolean;
}

export const usePersonaMessages = (
  personaId: number | undefined,
  timeRange: DateRangePickerValue
) => {
  const url = buildApiPath(`/api/analytics/admin/persona/messages`, {
    persona_id: personaId?.toString(),
    start: convertDateToStartOfDay(timeRange.from)?.toISOString(),
    end: convertDateToEndOfDay(timeRange.to)?.toISOString(),
  });

  const { data, error, isLoading } = useSWR<PersonaMessageAnalytics[]>(
    personaId !== undefined ? url : null,
    errorHandlingFetcher
  );

  return {
    data,
    error,
    isLoading,
    refreshPersonaMessages: () => mutate(url),
  };
};

export interface PersonaUniqueUserAnalytics {
  unique_users: number;
  date: string;
  persona_id: number;
}

export const usePersonaUniqueUsers = (
  personaId: number | undefined,
  timeRange: DateRangePickerValue
) => {
  const url = buildApiPath(`/api/analytics/admin/persona/unique-users`, {
    persona_id: personaId?.toString(),
    start: convertDateToStartOfDay(timeRange.from)?.toISOString(),
    end: convertDateToEndOfDay(timeRange.to)?.toISOString(),
  });

  const { data, error, isLoading } = useSWR<PersonaUniqueUserAnalytics[]>(
    personaId !== undefined ? url : null,
    errorHandlingFetcher
  );

  return {
    data,
    error,
    isLoading,
    refreshPersonaUniqueUsers: () => mutate(url),
  };
};

export const useChatSessionGroups = (
  timeRange: DateRangePickerValue,
  groupingType: GroupingType
) => {
  const url = "/api/admin/chat-session-groups";

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
