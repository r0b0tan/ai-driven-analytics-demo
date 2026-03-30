import { useCallback, useEffect, useState } from "react";
import { getLlmHealth, getModels, setProvider } from "../api/client";
import type { ModelOptions, ProviderInfo } from "../types";

interface Props {
  onProviderChange?: (info: ProviderInfo) => void;
}

export default function ModelSelector({ onProviderChange }: Props) {
  const [options, setOptions] = useState<ModelOptions | null>(null);
  const [selected, setSelected] = useState<ProviderInfo>({
    provider: "groq",
    model: "llama-3.3-70b-versatile",
  });
  const [health, setHealth] = useState<boolean | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const opts = await getModels();
      setOptions(opts);
      setSelected(opts.current);
    } catch {
      setError("Could not load model options.");
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    let cancelled = false;
    getLlmHealth().then((r) => {
      if (!cancelled) setHealth(r.healthy);
    }).catch(() => setHealth(false));
    return () => { cancelled = true; };
  }, [selected]);

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      const info = await setProvider(selected.provider, selected.model);
      setSelected(info);
      onProviderChange?.(info);
      const h = await getLlmHealth();
      setHealth(h.healthy);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Unknown error";
      setError(`Failed to update provider: ${msg}`);
    } finally {
      setSaving(false);
    }
  };

  const currentModels =
    options?.models?.[selected.provider] ?? [];

  return (
    <div className="model-selector">
      <h3 className="model-selector__title">Model Provider</h3>

      <div className="model-selector__field">
        <label>Provider</label>
        <div className="model-selector__radio-group">
          <label className="model-selector__radio-label">
            <input type="radio" name="provider" value="groq" checked readOnly />
            Groq (Cloud)
          </label>
        </div>
      </div>

      <div className="model-selector__field">
        <label htmlFor="model-select">Model</label>
        <select
          id="model-select"
          value={selected.model}
          onChange={(e) =>
            setSelected((prev) => ({ ...prev, model: e.target.value }))
          }
        >
          {currentModels.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
      </div>

      {error && <p className="model-selector__error">{error}</p>}

      <div className="model-selector__footer">
        <div className="model-selector__health">
          <span
            className={`status-dot ${
              health === null ? "status-dot--unknown" :
              health ? "status-dot--ok" : "status-dot--error"
            }`}
          />
          {health === null ? "checking…" : health ? "connected" : "unreachable"}
        </div>
        <button
          className="btn btn--primary"
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? "Applying…" : "Apply"}
        </button>
      </div>
    </div>
  );
}
