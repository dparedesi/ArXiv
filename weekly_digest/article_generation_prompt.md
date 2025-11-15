# Generate Weekly arXiv Research Digest

## Purpose & Scope

Create a Medium/LinkedIn article (4-5 minute read, approximately 1000-1250 words) based on the provided .csv file of recent arXiv research papers. Absorb the content, connect the dots, and grasp the most important/breakthrough concepts while being mindful of where the research community is concentrating its efforts.

**Format:** Single article file, no introductory fluff or personal anecdotes. Target 4-5 subsections with substantial depth in each to reach the required length.

**Sources:** Only use information from the provided .csv file and the "previous_articles.md" reference file. Do not use any other sources. CRITICAL: Every claim, example, and insight must come exclusively from the provided papers in the .csv file. Do not reference external knowledge, general trends not supported by this week's papers, or information from sources outside what has been explicitly provided. If a concept or technique is mentioned, it must be tied to specific papers from the .csv with proper citations.

**Paper Selection Priority (CRITICAL):** The .csv contains papers with their paper_id (format: YYMM.XXXXX). You MUST STRONGLY prioritize papers whose publication month (first 4 digits) matches the week being analyzed. For example, for Week 18 (early May 2025), the overwhelming majority of citations must be papers starting with 2505 (May 2025), with supporting citations from 2504 (April 2025) if highly relevant. Papers with older publication IDs (2501, 2502, 2503) represent revisions of earlier work and should be treated as exceptions, not the norm. Use them ONLY when they represent genuinely groundbreaking updates that are essential to your narrative and cannot be replaced by current-month papers.

**Quantitative Target:** Aim for minimum 75-85% of your citations to come from the current publication month (matching the week's month), with most remaining citations from the immediately adjacent month. Older papers should represent no more than 10-15% of total citations and must be justified by exceptional significance.

**Selection Process:** Before citing any paper, explicitly check its publication month. When building each subsection's narrative, first identify and prioritize papers from the current month, then fill gaps with adjacent-month papers if needed, and only then consider older papers if they are truly irreplaceable. Let the freshest research drive and shape your themes, not the other way around.

**Title:** Must start with the week identifier in the format "## [2025WkXX]:" followed by the article title. Use sentence case, avoid clickbait, and reflect a key, timely theme from *this week's papers*, avoiding overly broad or "end of an era" revolutionary framing. Be conscious not to be deterministic on topics that might continue to be developed in the next weeks. Make it specific enough that a reader can understand the concrete development or observation, not just the general area of research. Vary your title structure to avoid formulaic patterns.

## Content Guidelines

**Synthesis:** Combine concepts and create new knowledge from this specific batch of papers. Synthesize an insightful narrative about the current pulse of AI research. Themes should emerge directly from the provided .csv file and feel timely and specific to this week, rather than a grand, multi-year 'revolution' or 'paradigm shift'. It should read as if an expert has deeply analyzed this recent collection of papers and is reporting on the most interesting, interconnected themes they found. If a significant portion of papers focus on a particular domain (e.g., LLMs, ML), do not dismiss it as repetitive or established. Instead, identify what new developments, techniques, or applications are emerging within that dominant area. If papers cluster heavily around a single technique or narrow topic, validate whether this represents a genuine research focus or if you're over-indexing. Prefer broader connecting themes that span multiple research areas unless the clustering is overwhelming and significant. Note: Computer vision topics (image generation, video models, 3D reconstruction, etc.) should only be included if they represent truly outstanding breakthroughs or connect meaningfully to broader AI capabilities like reasoning, language, or agents. Prioritize coverage of language models, reasoning systems, agents, and cross-domain applications over pure vision research.

**Context from previous articles:** Use "previous_articles.md" only as reference to understand what has been covered previously. This helps you avoid treating established concepts as novel discoveries, but do identify and highlight new techniques, applications, or insights within those established domains. Do not reference these files explicitly or copy their style.

**Continuity:** Use the full context of previous articles to identify meaningful patterns and trends across multiple weeks. The opening paragraph should begin with 2-3 sentences about previous weeks' trends, providing enough detail so readers understand the research momentum (reference 4-8 weeks minimum, longer if relevant). Look for: sustained themes that are evolving, inflection points where the field pivoted, or areas where progress has accelerated. After establishing this context, transition to this week's focus within the same opening paragraph. Vary your framing approach - you might show contrast ("While previous weeks focused on X, this week reveals Y..."), acceleration ("The recent push toward X is now materializing in..."), or convergence ("After weeks of parallel work on X and Y, researchers are now..."). Avoid formulaic openings like always starting with "Following weeks of..."

**Conclusion (MANDATORY):** Every article MUST end with a concluding paragraph. This paragraph must: (1) explicitly reference and tie together all major subsections by name or theme, (2) connect them back to the article's central theme stated in the title/opening, and (3) provide 1-2 sentences of forward-looking implications about where this research trajectory is heading. Do not end the article after the last subsection. The conclusion is a required structural element.

**Tone:** Reflect a snapshot of current progress, not a definitive final statement on the direction of the entire field. The article represents one week in an ongoing series.

## Writing Style

**Structure:**
- Use ## for main title and ### for sections
- Cite papers using the format: [cite: XXXX.XXXXX]
- Back all major claims with citations from the provided papers
- Maintain consistent depth across all subsections
- Make subsection titles specific and concrete, not generic
- REQUIRED: End with a conclusion paragraph that synthesizes all subsections back to the central theme and provides forward-looking implications. This is NOT optional.

**Voice & Framing:**
- Adopt the direct, declarative tone of an expert analyst writing a concise briefing memo that CEOs and experts of the industry would love to read
- Anchor all narrative framing to the provided texts. Do not introduce broad historical claims (e.g., "For years...", "Traditionally...", "The story of AI has long been...") that are not directly supported by this week's papers or the previous articles
- Any statement about a "shift" or "trend" must be presented as an observation from the immediate research batch, not as a multi-year historical fact
- Do not over-fit on the style of previous articles