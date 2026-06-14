import { redirect } from "next/navigation";

export default function Page() {
  redirect("/state/account-settings?tab=certificate-settings");
}
