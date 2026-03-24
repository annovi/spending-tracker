import { Account } from "@/types";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface AccountSelectProps {
  accounts: Account[];
  value?: number;
  onChange: (accountId: number | undefined) => void;
  triggerClassName?: string;
  placeholder?: string;
  noAccountLabel?: string;
}

export function AccountSelect({
  accounts,
  value,
  onChange,
  triggerClassName,
  placeholder = "Select account (optional)",
  noAccountLabel = "No account",
}: AccountSelectProps) {
  return (
    <Select
      value={value?.toString() ?? "no-account"}
      onValueChange={(v) => onChange(v && v !== "no-account" ? Number(v) : undefined)}
    >
      <SelectTrigger className={triggerClassName}>
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="no-account">{noAccountLabel}</SelectItem>
        {accounts.map((account) => (
          <SelectItem key={account.id} value={account.id.toString()}>
            {account.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
