const { useEffect, useMemo, useState } = React;

const defaultJson = `{
  "companyNameApplyJob": "Acme Corp",
  "name": "Jane Doe",
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
  const [templates, setTemplates] = useState([]);
  const [activeTemplate, setActiveTemplate] = useState("");
  const [outputDirectory, setOutputDirectory] = useState("");
  const [newTemplatePath, setNewTemplatePath] = useState("");
  const [status, setStatus] = useState({ type: "", message: "" });
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  async function loadSettings() {
    try {
      const response = await fetch("/api/settings");
      const data = await response.json();
      setTemplates(data.templates || []);
      setActiveTemplate(data.activeTemplate || "");
      setOutputDirectory(data.outputDirectory || "");
    } catch (error) {
      setStatus({ type: "error", message: `Unable to load settings: ${error.message}` });
    }
  }

  async function persistSettings(nextTemplates, nextActiveTemplate, nextOutputDirectory) {
    const settings = {
      templates: nextTemplates,
      activeTemplate: nextActiveTemplate,
      outputDirectory: nextOutputDirectory,
    };
    await fetch("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(settings),
    });
  }

  async function handleAddTemplate() {
    const trimmed = newTemplatePath.trim();
    if (!trimmed) {
      setStatus({ type: "error", message: "Please enter a DOCX path before adding it." });
      return;
    }
    const nextTemplates = Array.from(new Set([...templates, trimmed]));
    const nextActiveTemplate = activeTemplate || trimmed;
    setTemplates(nextTemplates);
    setActiveTemplate(nextActiveTemplate);
    setNewTemplatePath("");
    await persistSettings(nextTemplates, nextActiveTemplate, outputDirectory);
    setStatus({ type: "success", message: `Added template: ${trimmed}` });
  }

  async function handleRemoveTemplate(templatePath) {
    const nextTemplates = templates.filter((item) => item !== templatePath);
    const nextActiveTemplate = activeTemplate === templatePath ? nextTemplates[0] || "" : activeTemplate;
    setTemplates(nextTemplates);
    setActiveTemplate(nextActiveTemplate);
    await persistSettings(nextTemplates, nextActiveTemplate, outputDirectory);
    setStatus({ type: "success", message: `Removed template: ${templatePath}` });
  }

  async function handleOutputDirectoryChange(event) {
    const nextValue = event.target.value;
    setOutputDirectory(nextValue);
    await persistSettings(templates, activeTemplate, nextValue);
  }

  async function handleGenerate() {
    setIsGenerating(true);
    setStatus({ type: "", message: "" });
    try {
      const response = await fetch("/api/generate-cv", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          jsonContent,
          templatePath: activeTemplate,
          outputDirectory,
        }),
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

  const canGenerate = useMemo(() => Boolean(jsonContent.trim()) && Boolean(activeTemplate), [jsonContent, activeTemplate]);

  return (
    <div className="card">
      <h1>CV Generator</h1>
      <p className="muted">Paste JSON data, choose a DOCX template, and generate a styled DOCX and PDF CV into your chosen folder.</p>

      <label><strong>JSON input</strong></label>
      <textarea value={jsonContent} onChange={(event) => setJsonContent(event.target.value)} />

      <div className="row">
        <div style={{ flex: 1 }}>
          <label><strong>DOCX template path</strong></label>
          <input type="text" value={newTemplatePath} onChange={(event) => setNewTemplatePath(event.target.value)} placeholder="/path/to/template.docx" />
        </div>
        <button className="secondary" onClick={handleAddTemplate}>Add template</button>
      </div>

      <div className="list">
        <label><strong>Template list</strong></label>
        {templates.length === 0 ? <p className="muted">No templates added yet.</p> : templates.map((templatePath) => (
          <div key={templatePath} className={`item ${templatePath === activeTemplate ? "active" : ""}`}>
            <span>{templatePath}</span>
            <div>
              <button className="secondary" onClick={() => setActiveTemplate(templatePath)}>Use</button>{' '}
              <button className="secondary" onClick={() => handleRemoveTemplate(templatePath)}>Remove</button>
            </div>
          </div>
        ))}
      </div>

      <div className="row">
        <div style={{ flex: 1 }}>
          <label><strong>Output directory</strong></label>
          <input type="text" value={outputDirectory} onChange={handleOutputDirectoryChange} placeholder="/path/to/output" />
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
