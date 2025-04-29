import * as React from "react";
import { CalendarIcon } from "lucide-react";
import { addDays, format } from "date-fns";
import { DateRange } from "react-day-picker";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { getXDaysAgo } from "./dateUtils";

export const TODAY = "today";
export const THIRTY_DAYS = "thirty_days";

export type DateRangePickerValue = {
  from: Date;
  to: Date;
  selectValue?: string;
};

export function DateRangeSelector({
  value,
  onValueChange,
}: {
  value: DateRangePickerValue;
  onValueChange: (value: DateRangePickerValue) => void;
}) {
  return (
    <div className="grid gap-2">
      <Popover>
        <PopoverTrigger asChild>
          <Button
            id="date"
            variant={"outline"}
            className={cn(
              "w-[240px] justify-start text-left font-normal",
              !value && "text-muted-foreground"
            )}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {value?.from ? (
              value.to ? (
                <>
                  {format(value.from, "LLL dd, y")} -{" "}
                  {format(value.to, "LLL dd, y")}
                </>
              ) : (
                format(value.from, "LLL dd, y")
              )
            ) : (
              <span>Pick a date</span>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="end">
          <Select
            value={value?.selectValue || THIRTY_DAYS}
            onValueChange={(selectValue) => {
              if (selectValue === TODAY) {
                const today = new Date();
                onValueChange({ from: today, to: today, selectValue });
              } else if (selectValue === THIRTY_DAYS) {
                onValueChange({
                  from: getXDaysAgo(30),
                  to: new Date(),
                  selectValue,
                });
              }
            }}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent position="popper">
              <SelectItem value={TODAY}>Today</SelectItem>
              <SelectItem value={THIRTY_DAYS}>Last 30 days</SelectItem>
            </SelectContent>
          </Select>
          <Calendar
            initialFocus
            mode="range"
            defaultMonth={value?.from}
            selected={{
              from: value?.from,
              to: value?.to,
            }}
            onSelect={(range: DateRange | undefined) => {
              if (!range) return;
              onValueChange({
                from: range.from!,
                to: range.to ?? range.from!,
              });
            }}
            numberOfMonths={2}
          />
        </PopoverContent>
      </Popover>
    </div>
  );
}
