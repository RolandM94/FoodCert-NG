import { redirect } from "next/navigation";

export default function Page() {
  redirect("/federal/directory?tab=employers");
}
