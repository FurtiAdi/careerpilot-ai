"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

import {
    getTailoredResume,
    type TailoredResume,
} from "@/services/tailoredResumeService";

export default function TailoredResumePreviewPage() {
    const params = useParams<{ id: string }>();
    const resumeId = Number(params.id);
    const validResumeId = Number.isInteger(resumeId) && resumeId > 0;

    const [resume, setResume] = useState<TailoredResume | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!validResumeId) {
            return;
        }

        let cancelled = false;

        const loadResume = async () => {
            try {
                const data = await getTailoredResume(resumeId);

                if (!cancelled) {
                    setResume(data);
                }
            } catch (error) {
                if (!cancelled) {
                    setError(
                        error instanceof Error
                            ? error.message
                            : "Failed to load tailored resume.",
                    );
                }
            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        };

        void loadResume();

        return () => {
            cancelled = true;
        };
    }, [resumeId, validResumeId]);

    if (!validResumeId) {
        return (
            <main className="min-h-screen bg-black px-6 pt-28 text-white">
                <p className="text-red-300">Invalid tailored resume ID.</p>
            </main>
        );
    }

    if (loading) {
        return (
            <main className="min-h-screen bg-black pt-40 text-center">
                <div className="inline-block h-10 w-10 animate-spin rounded-full border-4 border-purple-500/20 border-t-purple-400" />
            </main>
        );
    }

    if (error || !resume) {
        return (
            <main className="min-h-screen bg-black px-6 pt-28 text-white">
                <div className="mx-auto max-w-3xl rounded-2xl border border-red-500/30 bg-red-500/10 p-6">
                    <p className="text-red-200">
                        {error ?? "Tailored resume not found."}
                    </p>

                    <Link
                        href="/history"
                        className="mt-4 inline-block text-purple-300 hover:text-purple-200"
                    >
                        Return to analysis history
                    </Link>
                </div>
            </main>
        );
    }

    const { content, match_snapshot: match } = resume;
    const contactDetails = [
        content.contact.email,
        content.contact.phone,
        content.contact.location,
    ].filter(Boolean);

    return (
        <main className="min-h-screen bg-black px-6 py-28 text-white">
            <div className="mx-auto max-w-5xl">
                <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
                    <div>
                        <p className="text-sm text-purple-300">
                            Version {resume.version_number} · {resume.status}
                        </p>

                        <h1 className="mt-2 text-4xl font-bold">Tailored Resume Preview</h1>
                    </div>

                    <Link
                        href="/history"
                        className="rounded-xl border border-white/10 px-4 py-2 text-gray-300 hover:border-purple-500/40"
                    >
                        Back to history
                    </Link>
                </div>

                <article className="rounded-3xl bg-white p-8 text-gray-900 shadow-2xl md:p-12">
                    <header className="border-b border-gray-200 pb-6 text-center">
                        <h2 className="text-3xl font-bold">
                            {content.contact.full_name ?? "Tailored Resume"}
                        </h2>

                        {contactDetails.length > 0 && (
                            <p className="mt-3 text-sm text-gray-600">
                                {contactDetails.join(" · ")}
                            </p>
                        )}

                        {content.contact.links.length > 0 && (
                            <p className="mt-2 text-sm text-gray-600">
                                {content.contact.links.join(" · ")}
                            </p>
                        )}
                    </header>

                    {content.summary && (
                        <section className="mt-8">
                            <h3 className="text-lg font-bold uppercase tracking-wide">
                                Professional Summary
                            </h3>

                            <p className="mt-3 leading-7 text-gray-700">{content.summary}</p>
                        </section>
                    )}

                    {content.skills.length > 0 && (
                        <section className="mt-8">
                            <h3 className="text-lg font-bold uppercase tracking-wide">
                                Skills
                            </h3>

                            <p className="mt-3 leading-7 text-gray-700">
                                {content.skills.join(" · ")}
                            </p>
                        </section>
                    )}

                    {content.experience.length > 0 && (
                        <section className="mt-8">
                            <h3 className="text-lg font-bold uppercase tracking-wide">
                                Experience
                            </h3>

                            <div className="mt-4 space-y-6">
                                {content.experience.map((item, index) => (
                                    <div key={`${item.employer}-${item.title}-${index}`}>
                                        <div className="flex flex-wrap justify-between gap-2">
                                            <div>
                                                <h4 className="font-semibold">{item.title}</h4>

                                                <p className="text-gray-700">
                                                    {item.employer}
                                                    {item.location ? ` · ${item.location}` : ""}
                                                </p>
                                            </div>

                                            {(item.start_date || item.end_date) && (
                                                <p className="text-sm text-gray-500">
                                                    {item.start_date ?? ""}
                                                    {item.start_date && item.end_date ? " – " : ""}
                                                    {item.end_date ?? ""}
                                                </p>
                                            )}
                                        </div>

                                        {item.bullets.length > 0 && (
                                            <ul className="mt-3 list-disc space-y-2 pl-5 text-gray-700">
                                                {item.bullets.map((bullet, bulletIndex) => (
                                                    <li key={`${bullet}-${bulletIndex}`}>{bullet}</li>
                                                ))}
                                            </ul>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </section>
                    )}

                    {content.education.length > 0 && (
                        <section className="mt-8">
                            <h3 className="text-lg font-bold uppercase tracking-wide">
                                Education
                            </h3>

                            <div className="mt-4 space-y-5">
                                {content.education.map((item, index) => (
                                    <div key={`${item.institution}-${index}`}>
                                        <h4 className="font-semibold">{item.institution}</h4>

                                        {(item.degree || item.field_of_study) && (
                                            <p className="text-gray-700">
                                                {[item.degree, item.field_of_study]
                                                    .filter(Boolean)
                                                    .join(", ")}
                                            </p>
                                        )}

                                        {(item.start_date || item.end_date) && (
                                            <p className="text-sm text-gray-500">
                                                {[item.start_date, item.end_date]
                                                    .filter(Boolean)
                                                    .join(" – ")}
                                            </p>
                                        )}

                                        {item.details.length > 0 && (
                                            <ul className="mt-2 list-disc pl-5 text-gray-700">
                                                {item.details.map((detail, detailIndex) => (
                                                    <li key={`${detail}-${detailIndex}`}>{detail}</li>
                                                ))}
                                            </ul>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </section>
                    )}

                    {content.projects.length > 0 && (
                        <section className="mt-8">
                            <h3 className="text-lg font-bold uppercase tracking-wide">
                                Projects
                            </h3>

                            <div className="mt-4 space-y-5">
                                {content.projects.map((project, index) => (
                                    <div key={`${project.name}-${index}`}>
                                        <h4 className="font-semibold">{project.name}</h4>

                                        {project.description && (
                                            <p className="mt-1 text-gray-700">
                                                {project.description}
                                            </p>
                                        )}

                                        {project.technologies.length > 0 && (
                                            <p className="mt-1 text-sm text-gray-500">
                                                {project.technologies.join(" · ")}
                                            </p>
                                        )}

                                        {project.bullets.length > 0 && (
                                            <ul className="mt-2 list-disc pl-5 text-gray-700">
                                                {project.bullets.map((bullet, bulletIndex) => (
                                                    <li key={`${bullet}-${bulletIndex}`}>{bullet}</li>
                                                ))}
                                            </ul>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </section>
                    )}

                    {content.optional_sections.map((section, index) => (
                        <section key={`${section.heading}-${index}`} className="mt-8">
                            <h3 className="text-lg font-bold uppercase tracking-wide">
                                {section.heading}
                            </h3>

                            <ul className="mt-3 list-disc space-y-2 pl-5 text-gray-700">
                                {section.items.map((item, itemIndex) => (
                                    <li key={`${item}-${itemIndex}`}>{item}</li>
                                ))}
                            </ul>
                        </section>
                    ))}
                </article>

                {(resume.emphasized_items.length > 0 ||
                    resume.reordered_items.length > 0) && (
                        <section className="mt-8 rounded-3xl border border-purple-500/20 bg-purple-500/10 p-6">
                            <h2 className="text-xl font-semibold text-purple-200">
                                How this resume was tailored
                            </h2>

                            <div className="mt-5 grid gap-6 md:grid-cols-2">
                                {resume.emphasized_items.length > 0 && (
                                    <div>
                                        <h3 className="font-semibold text-white">
                                            Emphasized
                                        </h3>

                                        <ul className="mt-3 list-disc space-y-2 pl-5 text-gray-300">
                                            {resume.emphasized_items.map((item, index) => (
                                                <li key={`${item}-${index}`}>
                                                    {item}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                )}

                                {resume.reordered_items.length > 0 && (
                                    <div>
                                        <h3 className="font-semibold text-white">
                                            Reordered
                                        </h3>

                                        <ul className="mt-3 list-disc space-y-2 pl-5 text-gray-300">
                                            {resume.reordered_items.map((item, index) => (
                                                <li key={`${item}-${index}`}>
                                                    {item}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        </section>
                    )}
                <section className="mt-8 rounded-3xl border border-amber-500/20 bg-amber-500/10 p-6">
                    <h2 className="text-xl font-semibold text-amber-200">
                        Remaining skill gaps
                    </h2>

                    <p className="mt-2 text-sm text-gray-400">
                        These deterministic gaps were not added as claimed skills.
                    </p>

                    <div className="mt-4 flex flex-wrap gap-2">
                        {[
                            ...match.missing_required_skills,
                            ...match.missing_preferred_skills,
                        ].map((skill) => (
                            <span
                                key={skill}
                                className="rounded-full border border-amber-500/30 px-3 py-1 text-sm text-amber-100"
                            >
                                {skill}
                            </span>
                        ))}

                        {match.missing_required_skills.length === 0 &&
                            match.missing_preferred_skills.length === 0 && (
                                <p className="text-green-300">No identified skill gaps.</p>
                            )}
                    </div>
                </section>
            </div>
        </main>
    );
}
