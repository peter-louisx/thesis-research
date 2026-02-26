const { execSync } = require("child_process");
const fs = require("fs");


// ============================================================
// CONFIG - Add/remove queries here
// ============================================================
const TWITTER_AUTH_TOKEN = "ff3862f3dfd3ce723b5515ee625821a136605ddb"; // <-- paste your token here
const LIMIT = 2000;
const EXPORT_FORMAT = "csv";

const queries = {
  Danantara: [
    // "Danantara since:2025-03-26 until:2025-04-01 lang:id",
    // "Danantara since:2025-04-02 until:2025-04-08 lang:id",
    // "Danantara since:2025-04-09 until:2025-04-15 lang:id",
    // "Danantara since:2025-04-16 until:2025-04-22 lang:id",
    // "Danantara since:2025-04-23 until:2025-04-29 lang:id",
    // "Danantara since:2025-04-30 until:2025-05-06 lang:id",
    // "Danantara since:2025-05-07 until:2025-05-13 lang:id",
    // "Danantara since:2025-05-14 until:2025-05-20 lang:id",
    // "Danantara since:2025-05-21 until:2025-05-27 lang:id",
    // "Danantara since:2025-05-28 until:2025-06-03 lang:id",
    // "Danantara since:2025-06-04 until:2025-06-10 lang:id",
    "Danantara since:2025-06-11 until:2025-06-17 lang:id",
    "Danantara since:2025-06-18 until:2025-06-24 lang:id",
    "Danantara since:2025-06-25 until:2025-07-01 lang:id",
    "Danantara since:2025-07-02 until:2025-07-08 lang:id",
    "Danantara since:2025-07-09 until:2025-07-15 lang:id",
    "Danantara since:2025-07-16 until:2025-07-22 lang:id",
    "Danantara since:2025-07-23 until:2025-07-29 lang:id",
    "Danantara since:2025-07-30 until:2025-08-05 lang:id",
    "Danantara since:2025-08-06 until:2025-08-12 lang:id",
    "Danantara since:2025-08-13 until:2025-08-19 lang:id",
    "Danantara since:2025-08-20 until:2025-08-26 lang:id",
    "Danantara since:2025-08-27 until:2025-09-02 lang:id",
    "Danantara since:2025-09-03 until:2025-09-09 lang:id",
    "Danantara since:2025-09-10 until:2025-09-16 lang:id",
    "Danantara since:2025-09-17 until:2025-09-23 lang:id",
    "Danantara since:2025-09-24 until:2025-09-30 lang:id",
    "Danantara since:2025-10-01 until:2025-10-07 lang:id",
    "Danantara since:2025-10-08 until:2025-10-14 lang:id",
    "Danantara since:2025-10-15 until:2025-10-21 lang:id",
    "Danantara since:2025-10-22 until:2025-10-28 lang:id",
    "Danantara since:2025-10-29 until:2025-11-04 lang:id",
    "Danantara since:2025-11-05 until:2025-11-11 lang:id",
    "Danantara since:2025-11-12 until:2025-11-18 lang:id",
    "Danantara since:2025-11-19 until:2025-11-25 lang:id",
    "Danantara since:2025-11-26 until:2025-12-02 lang:id",
    "Danantara since:2025-12-03 until:2025-12-09 lang:id",
    "Danantara since:2025-12-10 until:2025-12-16 lang:id",
    "Danantara since:2025-12-17 until:2025-12-23 lang:id",
    "Danantara since:2025-12-24 until:2025-12-31 lang:id",
  ],
};

// ============================================================
// RUNNER - No need to edit below this line
// ============================================================
async function main() {
  const allQueries = Object.entries(queries).flatMap(([topic, queryList]) =>
    queryList.map((query) => ({ topic, query }))
  );

  const total = allQueries.length;
  console.log(`\nStarting automated scrape: ${total} queries total\n`);

  for (let i = 0; i < allQueries.length; i++) {
    const { topic, query } = allQueries[i];
    console.log(`\n[${i + 1}/${total}] Scraping: ${query}`);

    // Use the query as the output filename so each week gets its own file
    const outputFilename = query.replace(/[^a-zA-Z0-9_\-]/g, "_");

    const command = [
      `npx tweet-harvest`,
      `--token "${TWITTER_AUTH_TOKEN}"`,
      `--search-keyword "${query}"`,
      `--limit ${LIMIT}`,
      `--output-filename "${outputFilename}"`,
      `--export-format ${EXPORT_FORMAT}`,
      `--tab LATEST`,
    ].join(" ");

    try {
      execSync(command, { stdio: "inherit" });
      console.log(`\n✓ Done: ${query}`);
    } catch (err) {
      console.error(`\n✗ Failed: ${query}`);
      console.error(err.message);
      fs.appendFileSync("failed-queries.txt", query + "\n");
    }

    // Small delay between runs to avoid rate limiting
    if (i < allQueries.length - 1) {
      console.log(`\nWaiting 2 minutes before next query...`);
      await new Promise((res) => setTimeout(res, 120000));
    }
  }

  console.log(`\n✅ All done! Check your tweets-data folder.`);
}

main();