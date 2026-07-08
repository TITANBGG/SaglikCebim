import React, { useState, useEffect } from "react";
import { Activity, User, HeartPulse, Pill, Search, Plus, Trash2, ChevronRight, ChevronLeft, Save, AlertTriangle } from "lucide-react";
import client from "../../api/client";

interface Profile {
  age: string;
  gender: string;
  height: string;
  weight: string;
  blood_type: string;
}

interface Condition {
  id: string;
  condition_name: string;
  diagnosis_date: string;
}

interface Medication {
  id: string;
  medication_name: string;
  dosage: string;
  start_date: string;
}

interface Allergy {
  id: string;
  allergen_name: string;
  reaction_type: string;
}

export function Anamnez() {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(true);
  
  const [profile, setProfile] = useState<Profile>({ age: "", gender: "", height: "", weight: "", blood_type: "" });
  const [conditions, setConditions] = useState<Condition[]>([]);
  const [medications, setMedications] = useState<Medication[]>([]);
  const [allergies, setAllergies] = useState<Allergy[]>([]);

  // Inputs for new items
  const [newCond, setNewCond] = useState({ name: "", date: "" });
  const [newMed, setNewMed] = useState({ name: "", dosage: "", date: "" });
  const [newAllergy, setNewAllergy] = useState({ name: "", reaction: "" });
  const [pharmacySubstance, setPharmacySubstance] = useState("");
  const [pharmacyResult, setPharmacyResult] = useState<any>(null);
  const [pharmacyLoading, setPharmacyLoading] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [profRes, condRes, medRes, allRes] = await Promise.all([
        client.get("/api/v1/anamnesis/profile"),
        client.get("/api/v1/anamnesis/conditions"),
        client.get("/api/v1/anamnesis/medications"),
        client.get("/api/v1/anamnesis/allergies")
      ]);
      if(profRes.data.age !== undefined) setProfile(profRes.data);
      setConditions(condRes.data);
      setMedications(medRes.data);
      setAllergies(allRes.data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const saveProfile = async () => {
    try {
      await client.put("/api/v1/anamnesis/profile", profile);
    } catch {
      console.error("Profil kaydedilemedi");
    }
  };

  const addCondition = async () => {
    if (!newCond.name) return;
    const res = await client.post("/api/v1/anamnesis/conditions", { condition_name: newCond.name, diagnosis_date: newCond.date });
    setConditions([...conditions, { id: res.data.id, condition_name: newCond.name, diagnosis_date: newCond.date }]);
    setNewCond({ name: "", date: "" });
  };

  const deleteCondition = async (id: string) => {
    await client.delete(`/api/v1/anamnesis/conditions/${id}`);
    setConditions(conditions.filter(c => c.id !== id));
  };

  const addMedication = async () => {
    if (!newMed.name) return;
    const res = await client.post("/api/v1/anamnesis/medications", { medication_name: newMed.name, dosage: newMed.dosage, start_date: newMed.date });
    setMedications([...medications, { id: res.data.id, medication_name: newMed.name, dosage: newMed.dosage, start_date: newMed.date }]);
    setNewMed({ name: "", dosage: "", date: "" });
  };

  const deleteMedication = async (id: string) => {
    await client.delete(`/api/v1/anamnesis/medications/${id}`);
    setMedications(medications.filter(m => m.id !== id));
  };

  const checkPharmacy = async () => {
    if (!pharmacySubstance.trim()) return;
    setPharmacyLoading(true);
    try {
      const res = await client.post("/api/v1/anamnesis/pharmacy-check", { substance_name: pharmacySubstance.trim() });
      setPharmacyResult(res.data);
    } finally {
      setPharmacyLoading(false);
    }
  };

  const addAllergy = async () => {
    if (!newAllergy.name) return;
    const res = await client.post("/api/v1/anamnesis/allergies", { allergen_name: newAllergy.name, reaction_type: newAllergy.reaction });
    setAllergies([...allergies, { id: res.data.id, allergen_name: newAllergy.name, reaction_type: newAllergy.reaction }]);
    setNewAllergy({ name: "", reaction: "" });
  };

  const deleteAllergy = async (id: string) => {
    await client.delete(`/api/v1/anamnesis/allergies/${id}`);
    setAllergies(allergies.filter(a => a.id !== id));
  };

  const nextStep = () => {
    if (step === 1) saveProfile();
    if (step === 4) {
      window.location.href = "/dashboard";
    } else {
      setStep(s => Math.min(4, s + 1));
    }
  };
  const prevStep = () => setStep(s => Math.max(1, s - 1));

  if (loading) return <div className="text-white">Yükleniyor...</div>;

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Activity className="w-8 h-8 text-cyan-400" />
          Klinik Öykü (Anamnez)
        </h1>
        <p className="text-slate-400 mt-2">
          Multimodal yapay zeka ajanlarımız (Teşhis, Farmakoloji) bu verileri kullanarak size en doğru analizi sunacaktır.
        </p>
      </div>

      {/* Stepper */}
      <div className="flex items-center justify-between mb-8 bg-slate-800/50 p-4 rounded-xl border border-slate-700/50">
        {[
          { num: 1, label: "Profil", icon: User },
          { num: 2, label: "Özgeçmiş", icon: HeartPulse },
          { num: 3, label: "İlaç & Alerji", icon: Pill },
          { num: 4, label: "Soygeçmiş", icon: Activity }
        ].map(s => (
          <div key={s.num} className={`flex items-center gap-2 ${step >= s.num ? "text-cyan-400" : "text-slate-500"}`}>
            <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 ${step >= s.num ? "border-cyan-400 bg-cyan-950/30" : "border-slate-600"}`}>
              <s.icon className="w-5 h-5" />
            </div>
            <span className="font-medium hidden sm:block">{s.label}</span>
          </div>
        ))}
      </div>

      <div className="bg-slate-800/40 rounded-2xl border border-slate-700/50 p-6 min-h-[400px]">
        {/* Step 1 */}
        {step === 1 && (
          <div className="space-y-6 animate-in fade-in">
            <h2 className="text-xl font-semibold text-white">Temel Vücut Verileri</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-slate-400 mb-1">Yaş</label>
                <input type="number" value={profile.age || ""} onChange={e => setProfile({...profile, age: e.target.value})} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white" placeholder="Örn: 35" />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">Cinsiyet</label>
                <select value={profile.gender || ""} onChange={e => setProfile({...profile, gender: e.target.value})} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white">
                  <option value="">Seçiniz</option>
                  <option value="Male">Erkek</option>
                  <option value="Female">Kadın</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">Boy (cm)</label>
                <input type="number" value={profile.height || ""} onChange={e => setProfile({...profile, height: e.target.value})} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white" placeholder="Örn: 175" />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">Kilo (kg)</label>
                <input type="number" value={profile.weight || ""} onChange={e => setProfile({...profile, weight: e.target.value})} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white" placeholder="Örn: 70" />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">Kan Grubu</label>
                <select value={profile.blood_type || ""} onChange={e => setProfile({...profile, blood_type: e.target.value})} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white">
                  <option value="">Seçiniz</option>
                  <option value="A+">A+</option><option value="A-">A-</option>
                  <option value="B+">B+</option><option value="B-">B-</option>
                  <option value="AB+">AB+</option><option value="AB-">AB-</option>
                  <option value="0+">0+</option><option value="0-">0-</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Step 2 */}
        {step === 2 && (
          <div className="space-y-6 animate-in fade-in">
            <h2 className="text-xl font-semibold text-white">Özgeçmiş (Kronik Hastalıklar)</h2>
            <p className="text-slate-400 text-sm">Diagnosis (Teşhis) ajanımız bu hastalıklarınızı göz önünde bulundurarak analiz yapacaktır.</p>
            
            <div className="flex gap-2">
              <input type="text" placeholder="Hastalık / Ameliyat (Örn: Hipertansiyon)" value={newCond.name} onChange={e => setNewCond({...newCond, name: e.target.value})} className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white" />
              <input type="text" placeholder="Teşhis Yılı" value={newCond.date} onChange={e => setNewCond({...newCond, date: e.target.value})} className="w-32 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white" />
              <button onClick={addCondition} className="bg-cyan-600 hover:bg-cyan-500 text-white px-4 py-2 rounded-lg"><Plus className="w-5 h-5" /></button>
            </div>

            <div className="space-y-2 mt-4">
              {conditions.map(c => (
                <div key={c.id} className="flex items-center justify-between bg-slate-900/50 border border-slate-700/50 p-3 rounded-lg">
                  <div>
                    <span className="text-white font-medium">{c.condition_name}</span>
                    {c.diagnosis_date && <span className="text-slate-400 text-sm ml-2">({c.diagnosis_date})</span>}
                  </div>
                  <button onClick={() => deleteCondition(c.id)} className="text-red-400 hover:text-red-300"><Trash2 className="w-4 h-4" /></button>
                </div>
              ))}
              {conditions.length === 0 && <div className="text-slate-500 text-center py-4">Kayıtlı hastalık bulunmuyor.</div>}
            </div>
          </div>
        )}

        {/* Step 3 */}
        {step === 3 && (
          <div className="space-y-8 animate-in fade-in">
            <div>
              <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                💊 Kullanılan İlaçlar <span className="text-xs bg-purple-500/20 text-purple-400 px-2 py-1 rounded-full border border-purple-500/30">Pharmacology Agent</span>
              </h2>
              <div className="flex gap-2 mt-4">
                <input type="text" placeholder="İlaç Adı (Örn: Metformin)" value={newMed.name} onChange={e => setNewMed({...newMed, name: e.target.value})} className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white" />
                <input type="text" placeholder="Doz (Örn: 1000mg)" value={newMed.dosage} onChange={e => setNewMed({...newMed, dosage: e.target.value})} className="w-32 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white" />
                <button onClick={addMedication} className="bg-cyan-600 hover:bg-cyan-500 text-white px-4 py-2 rounded-lg"><Plus className="w-5 h-5" /></button>
              </div>
              <div className="space-y-2 mt-3">
                {medications.map(m => (
                  <div key={m.id} className="flex items-center justify-between bg-slate-900/50 border border-slate-700/50 p-3 rounded-lg">
                    <div className="text-white font-medium">{m.medication_name} <span className="text-cyan-400 text-sm">{m.dosage}</span></div>
                    <button onClick={() => deleteMedication(m.id)} className="text-red-400 hover:text-red-300"><Trash2 className="w-4 h-4" /></button>
                  </div>
                ))}
              </div>

              <div className="mt-5 bg-cyan-950/20 border border-cyan-800/40 rounded-xl p-4">
                <div className="flex items-center justify-between gap-3 mb-3">
                  <div>
                    <h3 className="text-white font-semibold flex items-center gap-2">
                      <Search className="w-4 h-4 text-cyan-300" />
                      Pharmacy Etkileşim Kontrolü
                    </h3>
                    <p className="text-xs text-cyan-200/70 mt-1">Yeni ilaç/maddeyi mevcut ilaç listesiyle hızlıca karşılaştırır.</p>
                  </div>
                  <span className="text-[10px] text-cyan-200 border border-cyan-700 rounded-full px-2 py-1">Demo Matrix</span>
                </div>
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Örn: Aspirin, ibuprofen, alkol"
                    value={pharmacySubstance}
                    onChange={e => setPharmacySubstance(e.target.value)}
                    className="flex-1 bg-slate-950 border border-cyan-900/60 rounded-lg px-4 py-2 text-white"
                  />
                  <button
                    onClick={checkPharmacy}
                    disabled={pharmacyLoading}
                    className="bg-cyan-600 hover:bg-cyan-500 disabled:opacity-60 text-white px-4 py-2 rounded-lg"
                  >
                    Kontrol Et
                  </button>
                </div>
                {pharmacyResult && (
                  <div className={`mt-3 rounded-lg border p-3 text-sm ${pharmacyResult.status === "risk" ? "bg-red-950/30 border-red-800 text-red-100" : "bg-emerald-950/30 border-emerald-800 text-emerald-100"}`}>
                    <div className="font-semibold">{pharmacyResult.message}</div>
                    <div className="text-xs opacity-80 mt-1">Kontrol edilen: {pharmacyResult.checked_substance}</div>
                    {pharmacyResult.risks?.length > 0 && (
                      <ul className="list-disc pl-5 mt-2 space-y-1">
                        {pharmacyResult.risks.map((risk: any, idx: number) => (
                          <li key={idx}>{risk.severity}: {risk.message}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}
              </div>
            </div>

            <div className="pt-4 border-t border-slate-700/50">
              <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                ⚠️ Alerjiler <span className="text-xs bg-purple-500/20 text-purple-400 px-2 py-1 rounded-full border border-purple-500/30">Pharmacology Agent</span>
              </h2>
              <div className="flex gap-2 mt-4">
                <input type="text" placeholder="Alerjen (Örn: Penisilin, Fıstık)" value={newAllergy.name} onChange={e => setNewAllergy({...newAllergy, name: e.target.value})} className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white" />
                <input type="text" placeholder="Reaksiyon (Örn: Döküntü)" value={newAllergy.reaction} onChange={e => setNewAllergy({...newAllergy, reaction: e.target.value})} className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white" />
                <button onClick={addAllergy} className="bg-cyan-600 hover:bg-cyan-500 text-white px-4 py-2 rounded-lg"><Plus className="w-5 h-5" /></button>
              </div>
              <div className="space-y-2 mt-3">
                {allergies.map(a => (
                  <div key={a.id} className="flex items-center justify-between bg-red-950/20 border border-red-900/30 p-3 rounded-lg">
                    <div className="text-red-200 font-medium">{a.allergen_name} <span className="text-slate-400 text-sm">- {a.reaction_type}</span></div>
                    <button onClick={() => deleteAllergy(a.id)} className="text-red-400 hover:text-red-300"><Trash2 className="w-4 h-4" /></button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Step 4 */}
        {step === 4 && (
          <div className="space-y-6 animate-in fade-in flex flex-col items-center justify-center text-center h-[300px]">
            <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mb-4">
              <Activity className="w-8 h-8 text-slate-500" />
            </div>
            <h2 className="text-2xl font-semibold text-slate-300">Soygeçmiş (Genetik Miras)</h2>
            <p className="text-slate-400 max-w-md">
              Bu alan gelecekteki <strong className="text-purple-400">Genetik & Risk Ajanımız</strong> için geliştirilme aşamasındadır. Ailedeki kalıtsal hastalıklar yakında sisteme entegre edilecektir.
            </p>
            <div className="bg-amber-900/20 text-amber-500/80 px-4 py-2 rounded-lg border border-amber-900/30 flex items-center gap-2 mt-4">
              <AlertTriangle className="w-5 h-5" /> Yapım Aşamasında
            </div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <div className="flex justify-between mt-6">
        <button
          onClick={prevStep}
          disabled={step === 1}
          className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-colors ${step === 1 ? "bg-slate-800 text-slate-600 cursor-not-allowed" : "bg-slate-800 text-white hover:bg-slate-700"}`}
        >
          <ChevronLeft className="w-5 h-5" /> Geri
        </button>
        <button
          onClick={nextStep}
          className="flex items-center gap-2 px-8 py-3 rounded-xl font-medium bg-cyan-600 text-white hover:bg-cyan-500 transition-colors shadow-lg shadow-cyan-900/20"
        >
          {step === 4 ? "Tamamla" : "İleri"} <ChevronRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
