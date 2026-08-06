const { useEffect, useMemo, useState } = React;

const defaultJson = `{
  "companyNameApplyJob": "Acme Corp",
  "personNameOnCV": "Jane Doe",
  "contact": "Berlin, Germany • jane.doe@example.com",
  "summary": "Experienced software engineer with a strong focus on product delivery and technical leadership.",
  "experience": [
    {
      "companyName": "Contoso",
      "jobTitle": "Senior Engineer",
      "startDate": "01/2021",
      "endDate": "Present",
      "content": ["Led the frontend platform", "Improved release velocity", "Mentored engineers"]
    }
  ],
  "skills": [
    { "categoryName": "Frontend", "skillItems": ["React", "TypeScript", "CSS"] }
  ],
  "education": [
    { "institution": "Technical University", "degree": "BSc Computer Science" }
  ]
}`;

function App() {
  const [jsonContent, setJsonContent] = useState(defaultJson);
  const [outputDirectory, setOutputDirectory] = useState("");
  const [status, setStatus] = useState({ type: "", message: "" });
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  async function loadSettings() {
    try {
      const response = await fetch("/api/settings");
      const data = await response.json();
      setOutputDirectory(data.outputDirectory || "");
    } catch (error) {
      setStatus({ type: "error", message: `Unable to load settings: ${error.message}` });
    }
  }

  async function persistSettings(nextOutputDirectory) {
    await fetch("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ outputDirectory: nextOutputDirectory }),
    });
  }

  async function handleOutputDirectoryChange(event) {
    const nextValue = event.target.value;
    setOutputDirectory(nextValue);
    await persistSettings(nextValue);
  }

  async function handleGenerate() {
    setIsGenerating(true);
    setStatus({ type: "", message: "" });
    try {
      const response = await fetch("/api/generate-cv", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jsonContent, outputDirectory }),
      });
      const data = await response.json();
      if (!response.ok || data.error) {
        throw new Error(data.error || "Generation failed.");
      }
      const base = `Created DOCX at ${data.docxPath} and PDF at ${data.pdfPath}`;
      setStatus({ type: "success", message: data.warning ? `${base} — ${data.warning}` : base });
    } catch (error) {
      setStatus({ type: "error", message: error.message || "Generation failed." });
    } finally {
      setIsGenerating(false);
    }
  }

  const canGenerate = useMemo(
    () => Boolean(jsonContent.trim()) && Boolean(outputDirectory.trim()),
    [jsonContent, outputDirectory]
  );

  return (
    <div className="card">
      <h1>CV Generator</h1>
      <p className="muted">Paste JSON data and choose an output base folder. The CV is generated from
        the bundled <code>cv_template.docx</code>, reusing its title, heading, text and bullet styles,
        and saved as a styled DOCX and PDF.</p>

      <label><strong>JSON input</strong></label>
      <textarea value={jsonContent} onChange={(event) => setJsonContent(event.target.value)} />

      <div className="row">
        <div style={{ flex: 1 }}>
          <label><strong>Output base folder</strong></label>
          <input type="text" value={outputDirectory} onChange={handleOutputDirectoryChange} placeholder="/path/to/output" />
          <p className="muted">Files are written to <code>&lt;base&gt;/&lt;yy_mm_dd&gt;/&lt;personNameOnCV&gt;_&lt;companyNameApplyJob&gt;.pdf</code> (and .docx).</p>
        </div>
      </div>

      <div className="row">
        <button onClick={handleGenerate} disabled={!canGenerate || isGenerating}>
          {isGenerating ? "Generating..." : "Generate CV (DOCX + PDF)"}
        </button>
      </div>
      {status.message ? <div className={`status ${status.type}`}>{status.message}</div> : null}
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
