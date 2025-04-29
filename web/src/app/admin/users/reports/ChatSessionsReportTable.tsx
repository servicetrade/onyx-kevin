import React from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ThreeDotsLoader } from "@/components/Loading";
import { ErrorCallout } from "@/components/ErrorCallout";
import { useChatSessionGroups } from "./hooks";
import { DateRangePickerValue } from "./DateRangeSelector";
import { GroupingType } from "./types";

export function ChatSessionsReportTable({
  timeRange,
  groupingType,
}: {
  timeRange: DateRangePickerValue;
  groupingType: GroupingType;
}) {
  const { data, error, isLoading } = useChatSessionGroups(
    timeRange,
    groupingType
  );

  if (error) {
    return (
      <ErrorCallout
        errorTitle="Error fetching chat session data"
        errorMsg={error?.message}
      />
    );
  }

  if (isLoading) {
    return <ThreeDotsLoader />;
  }

  if (!data || data.data.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-lg text-muted-foreground">
          No data available for the selected time range.
        </p>
      </div>
    );
  }

  return (
    <div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[60%]">
              {groupingType === "user" ? "User Email" : "Assistant Name"}
            </TableHead>
            <TableHead>Chat Sessions Count</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.data.map((item) => (
            <TableRow key={item.name}>
              <TableCell className="font-medium">{item.name}</TableCell>
              <TableCell>{item.count}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <div className="mt-4 text-sm text-muted-foreground">
        <p>
          Total rows: {data.total_rows} | Total chat sessions:{" "}
          {data.total_sessions}
        </p>
      </div>
    </div>
  );
}
