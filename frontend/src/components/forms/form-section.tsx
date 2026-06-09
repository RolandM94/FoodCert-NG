export function FormSection({
  title,
  description,
  children
}: {
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-lg border border-neutral-200 bg-white p-5 shadow-sm">
      <div className="mb-5">
        <h2 className="text-base font-bold text-neutral-900">{title}</h2>
        {description ? <p className="mt-1 text-sm text-neutral-600">{description}</p> : null}
      </div>
      <div className="grid gap-4">{children}</div>
    </section>
  );
}
