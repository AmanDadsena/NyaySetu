"use client";

import { useState } from "react";
import { CheckCircle2, AlertTriangle, Phone, ExternalLink, ShieldCheck, Scale } from "lucide-react";
import { SectionCard, Label, inputClass, buttonClass, postJSON } from "./shared";

interface LegalAidResult {
  eligible: boolean;
  category: string;
  statutory_clause: string;
  income_limit_applied: number | null;
  entitlements: string[];
  action_steps: string[];
  helpline: string;
  portal_url: string;
}

const INDIAN_STATES = [
  "Delhi",
  "Maharashtra",
  "Karnataka",
  "Tamil Nadu",
  "Telangana",
  "Andhra Pradesh",
  "Uttar Pradesh",
  "West Bengal",
  "Rajasthan",
  "Madhya Pradesh",
  "Gujarat",
  "Kerala",
  "Punjab",
  "Haryana",
  "Bihar",
  "Odisha",
  "Assam",
  "Chhattisgarh",
  "Jharkhand",
];

export function LegalAidTool({ onError }: { onError?: (msg: string | null) => void }) {
  const [isWomanOrChild, setIsWomanOrChild] = useState(false);
  const [isScSt, setIsScSt] = useState(false);
  const [isDisabled, setIsDisabled] = useState(false);
  const [isWorkman, setIsWorkman] = useState(false);
  const [isInCustody, setIsInCustody] = useState(false);
  const [isDisasterVictim, setIsDisasterVictim] = useState(false);
  const [annualIncome, setAnnualIncome] = useState<number>(180000);
  const [state, setState] = useState("Delhi");
  const [courtLevel, setCourtLevel] = useState("district");

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<LegalAidResult | null>(null);

  const assessEligibility = async () => {
    setLoading(true);
    onError?.(null);
    try {
      const data = await postJSON<LegalAidResult>("/api/tools/nalsa-aid", {
        is_woman_or_child: isWomanOrChild,
        is_sc_st: isScSt,
        is_disabled: isDisabled,
        is_industrial_workman: isWorkman,
        is_in_custody: isInCustody,
        is_disaster_victim: isDisasterVictim,
        annual_income: annualIncome,
        state: state.toLowerCase(),
        court_level: courtLevel,
      });
      setResult(data);
    } catch (err) {
      // Local statutory fallback if server is offline
      const eligible =
        isWomanOrChild ||
        isScSt ||
        isDisabled ||
        isWorkman ||
        isInCustody ||
        isDisasterVictim ||
        annualIncome <= 300000;

      setResult({
        eligible,
        category: isWomanOrChild
          ? "Woman or Child"
          : isScSt
          ? "Scheduled Caste / Scheduled Tribe"
          : "Income Qualified",
        statutory_clause: "Section 12, Legal Services Authorities Act, 1987",
        income_limit_applied: 300000,
        entitlements: [
          "Free legal representation by an assigned advocate",
          "Complete exemption from court and drafting fees",
          "Free certified copies of judicial orders",
        ],
        action_steps: [
          "Visit the District Legal Services Authority (DLSA) in your District Court complex",
          "Or register at your local Common Service Centre (CSC) via Tele-Law",
          "Call NALSA National Helpline at 15100",
        ],
        helpline: "15100 (NALSA 24x7 National Helpline)",
        portal_url: "https://nalsa.gov.in",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <SectionCard>
        <div className="flex items-center gap-3 mb-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900 text-white">
            <Scale className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900">NALSA Free Legal Aid & Tele-Law Screener</h2>
            <p className="text-xs text-gray-500">
              Statutory entitlement under Section 12, Legal Services Authorities Act, 1987.
            </p>
          </div>
        </div>

        <div className="mt-6 space-y-6">
          <div>
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider block mb-3">
              1. Statutory Priority Categories (Zero Income Barrier)
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              <label className="flex items-center gap-3 p-3 rounded-xl border border-gray-200 bg-gray-50/50 hover:bg-gray-100/60 cursor-pointer transition-colors">
                <input
                  type="checkbox"
                  checked={isWomanOrChild}
                  onChange={(e) => setIsWomanOrChild(e.target.checked)}
                  className="rounded border-gray-300 text-black focus:ring-black w-4 h-4"
                />
                <span className="text-sm font-medium text-gray-800">Woman or Child (under 18)</span>
              </label>

              <label className="flex items-center gap-3 p-3 rounded-xl border border-gray-200 bg-gray-50/50 hover:bg-gray-100/60 cursor-pointer transition-colors">
                <input
                  type="checkbox"
                  checked={isScSt}
                  onChange={(e) => setIsScSt(e.target.checked)}
                  className="rounded border-gray-300 text-black focus:ring-black w-4 h-4"
                />
                <span className="text-sm font-medium text-gray-800">Member of Scheduled Caste / Tribe</span>
              </label>

              <label className="flex items-center gap-3 p-3 rounded-xl border border-gray-200 bg-gray-50/50 hover:bg-gray-100/60 cursor-pointer transition-colors">
                <input
                  type="checkbox"
                  checked={isDisabled}
                  onChange={(e) => setIsDisabled(e.target.checked)}
                  className="rounded border-gray-300 text-black focus:ring-black w-4 h-4"
                />
                <span className="text-sm font-medium text-gray-800">Person with Disability (PwD)</span>
              </label>

              <label className="flex items-center gap-3 p-3 rounded-xl border border-gray-200 bg-gray-50/50 hover:bg-gray-100/60 cursor-pointer transition-colors">
                <input
                  type="checkbox"
                  checked={isWorkman}
                  onChange={(e) => setIsWorkman(e.target.checked)}
                  className="rounded border-gray-300 text-black focus:ring-black w-4 h-4"
                />
                <span className="text-sm font-medium text-gray-800">Industrial Workman</span>
              </label>

              <label className="flex items-center gap-3 p-3 rounded-xl border border-gray-200 bg-gray-50/50 hover:bg-gray-100/60 cursor-pointer transition-colors">
                <input
                  type="checkbox"
                  checked={isInCustody}
                  onChange={(e) => setIsInCustody(e.target.checked)}
                  className="rounded border-gray-300 text-black focus:ring-black w-4 h-4"
                />
                <span className="text-sm font-medium text-gray-800">In Custody / Undertrial Prisoner</span>
              </label>

              <label className="flex items-center gap-3 p-3 rounded-xl border border-gray-200 bg-gray-50/50 hover:bg-gray-100/60 cursor-pointer transition-colors">
                <input
                  type="checkbox"
                  checked={isDisasterVictim}
                  onChange={(e) => setIsDisasterVictim(e.target.checked)}
                  className="rounded border-gray-300 text-black focus:ring-black w-4 h-4"
                />
                <span className="text-sm font-medium text-gray-800">Victim of Disaster / Caste Atrocity</span>
              </label>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label>2. State of Residence</Label>
              <select
                value={state}
                onChange={(e) => setState(e.target.value)}
                className={inputClass}
              >
                {INDIAN_STATES.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <Label>3. Forum / Court Level</Label>
              <select
                value={courtLevel}
                onChange={(e) => setCourtLevel(e.target.value)}
                className={inputClass}
              >
                <option value="district">District / Subordinate Courts</option>
                <option value="high">High Court (HCLSC)</option>
                <option value="supreme">Supreme Court (SCLSC)</option>
              </select>
            </div>

            <div>
              <Label>4. Total Annual Income (₹)</Label>
              <input
                type="number"
                value={annualIncome}
                onChange={(e) => setAnnualIncome(Number(e.target.value) || 0)}
                className={inputClass}
                placeholder="e.g. 180000"
              />
            </div>
          </div>

          <button
            onClick={assessEligibility}
            disabled={loading}
            className={buttonClass}
          >
            {loading ? "Evaluating Criteria..." : "Evaluate Legal Aid Entitlement"}
          </button>
        </div>
      </SectionCard>

      {result && (
        <SectionCard className={result.eligible ? "border-emerald-200 bg-emerald-50/30" : "border-amber-200 bg-amber-50/30"}>
          <div className="space-y-5">
            <div className="flex items-start gap-3">
              {result.eligible ? (
                <ShieldCheck className="h-6 w-6 text-emerald-600 shrink-0 mt-0.5" />
              ) : (
                <AlertTriangle className="h-6 w-6 text-amber-600 shrink-0 mt-0.5" />
              )}
              <div>
                <h3 className="text-base font-bold text-slate-900">
                  {result.eligible
                    ? "Qualified: 100% Free Legal Representation Entitlement"
                    : "Income Exceeds Standard District Threshold"}
                </h3>
                <p className="text-xs text-gray-600 mt-0.5">
                  {result.statutory_clause} — Category: <span className="font-semibold text-slate-900">{result.category}</span>
                </p>
              </div>
            </div>

            {result.income_limit_applied && (
              <div className="rounded-xl border border-gray-200 bg-white p-3 text-xs text-gray-700 flex justify-between">
                <span>Statutory State Income Ceiling:</span>
                <span className="font-bold">₹{result.income_limit_applied.toLocaleString("en-IN")} / year</span>
              </div>
            )}

            {result.entitlements.length > 0 && (
              <div>
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2">
                  Guaranteed Statutory Benefits
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {result.entitlements.map((item, i) => (
                    <div
                      key={i}
                      className="flex items-start gap-2 p-2.5 rounded-lg border border-emerald-200 bg-white text-xs text-gray-800"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                      <span>{item}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div>
              <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2">
                Actionable Procedure
              </h4>
              <ol className="space-y-1.5 list-decimal list-inside text-xs text-gray-700">
                {result.action_steps.map((step, i) => (
                  <li key={i} className="p-2 rounded-lg bg-white border border-gray-200/80">
                    {step}
                  </li>
                ))}
              </ol>
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-xl border border-gray-200 bg-white">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-full bg-slate-100 text-slate-900">
                  <Phone className="w-4 h-4" />
                </div>
                <div>
                  <p className="text-[11px] text-gray-500">NALSA 24x7 National Helpline</p>
                  <p className="text-sm font-bold text-slate-900">Toll-Free 15100</p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <a
                  href="https://nalsa.gov.in"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-100 text-slate-900 hover:bg-slate-200 transition-colors flex items-center gap-1.5"
                >
                  NALSA Portal <ExternalLink className="w-3.5 h-3.5" />
                </a>
                <a
                  href="https://www.tele-law.in"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-900 text-white hover:bg-slate-800 transition-colors flex items-center gap-1.5"
                >
                  Tele-Law CSC <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>
            </div>
          </div>
        </SectionCard>
      )}
    </div>
  );
}
