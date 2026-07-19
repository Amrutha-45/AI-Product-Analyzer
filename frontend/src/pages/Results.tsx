import { useEffect, useState } from 'react';
import { useParams, Link, useLocation } from 'react-router-dom';
import { ArrowLeft, CheckCircle, AlertTriangle, AlertOctagon, Info, TrendingUp, TrendingDown, Shield } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Chip } from '../components/ui/Chip';
import { Gauge } from '../components/ui/Gauge';
import { scanService, type ScanResult, type ScoreBreakdownItem, type FoodScanResult, type MedicineScanResult, type CosmeticScanResult, type FertilizerScanResult, type PesticideScanResult, type HouseholdChemicalScanResult, type OtherScanResult } from '../services/api/scanService';

const NovaLabel: Record<number, { label: string; color: string }> = {
  1: { label: 'Unprocessed', color: 'text-accent' },
  2: { label: 'Minimally Processed', color: 'text-accent' },
  3: { label: 'Processed', color: 'text-accent-warning' },
  4: { label: 'Ultra-Processed', color: 'text-accent-danger' },
};

const getRiskIcon = (level: string) => {
  switch (level) {
    case 'safe': return <CheckCircle className="w-5 h-5 text-accent" />;
    case 'moderate': return <AlertTriangle className="w-5 h-5 text-accent-warning" />;
    case 'high': return <AlertOctagon className="w-5 h-5 text-accent-danger" />;
    default: return <Info className="w-5 h-5 text-text-secondary" />;
  }
};

const FoodResults = ({ data }: { data: FoodScanResult }) => {

  return (
    <>
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <Card className="flex flex-col items-center justify-center text-center">
          <h3 className="text-sm font-medium text-text-secondary mb-4 uppercase tracking-wider">Health Score</h3>
          <Gauge value={data.health_score} label="/ 100" />
          <p className="mt-3 text-xs text-text-secondary">Nutritional quality</p>
        </Card>
        <Card className="flex flex-col items-center justify-center text-center">
          <h3 className="text-sm font-medium text-text-secondary mb-4 uppercase tracking-wider">Safety Score</h3>
          <Gauge value={data.ingredient_safety_score} label="/ 100" colorClass="text-accent" />
          <p className="mt-3 text-xs text-text-secondary">Ingredient safety (GRAS/FSSAI)</p>
        </Card>
        <Card>
          <h3 className="text-sm font-medium text-text-secondary mb-3 uppercase tracking-wider">AI Summary</h3>
          <p className="text-white text-sm leading-relaxed mb-3">{data.ai_summary}</p>
          {data.ai_suggested_improvement && (
            <div className="p-3 bg-primary/10 rounded-xl border border-primary/20">
              <p className="text-xs text-primary font-medium flex items-center gap-1 mb-1">
                <Info className="w-3 h-3" /> Tip
              </p>
              <p className="text-xs text-white">{data.ai_suggested_improvement}</p>
            </div>
          )}
        </Card>
      </div>

      {data.health_score_breakdown.length > 0 && (
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-4">Health Score Breakdown</h2>
          <Card>
            <div className="flex flex-col gap-2">
              <div className="flex justify-between text-xs text-text-secondary uppercase tracking-wider pb-2 border-b border-base-700">
                <span>Factor</span>
                <span>Points</span>
              </div>
              <div className="flex justify-between text-sm py-1">
                <span className="text-text-secondary">Base score</span>
                <span className="text-white font-mono">70</span>
              </div>
              {data.health_score_breakdown.map((item: ScoreBreakdownItem, i: number) => (
                <div key={i} className="flex items-center justify-between py-1 border-b border-base-800/50">
                  <div className="flex items-center gap-2">
                    {item.points > 0
                      ? <TrendingUp className="w-4 h-4 text-accent flex-shrink-0" />
                      : <TrendingDown className="w-4 h-4 text-accent-danger flex-shrink-0" />}
                    <span className="text-sm text-white">{item.label}</span>
                  </div>
                  <span className={`font-mono font-bold text-sm ${item.points > 0 ? 'text-accent' : 'text-accent-danger'}`}>
                    {item.points > 0 ? '+' : ''}{item.points}
                  </span>
                </div>
              ))}
              <div className="flex justify-between text-sm pt-2 border-t border-base-700">
                <span className="font-bold text-white">Final Health Score</span>
                <span className="font-bold font-mono text-white">{data.health_score}</span>
              </div>
            </div>
          </Card>
        </div>
      )}

      {data.nutrition && (
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-4">Nutrition (per 100g)</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {([
              { label: 'Sugar', value: data.nutrition.sugar_per_100g, unit: 'g', threshold: 10 },
              { label: 'Sodium', value: data.nutrition.sodium_mg_per_100g, unit: 'mg', threshold: 300 },
              { label: 'Sat. Fat', value: data.nutrition.saturated_fat_per_100g, unit: 'g', threshold: 5 },
              { label: 'Fiber', value: data.nutrition.fiber_per_100g, unit: 'g', threshold: null },
              { label: 'Protein', value: data.nutrition.protein_per_100g, unit: 'g', threshold: null },
              { label: 'Caffeine', value: data.nutrition.caffeine_mg_per_serving, unit: 'mg/srv', threshold: 150 },
            ] as const).filter(n => n.value !== null && n.value !== undefined).map((n, i) => {
              const isHigh = n.threshold !== null && (n.value as number) > n.threshold;
              return (
                <Card key={i} className={`text-center p-4 ${isHigh ? 'border-accent-danger/30 bg-accent-danger/5' : ''}`}>
                  <p className="text-xs text-text-secondary uppercase tracking-wider mb-1">{n.label}</p>
                  <p className={`text-2xl font-bold ${isHigh ? 'text-accent-danger' : 'text-white'}`}>
                    {typeof n.value === 'number' ? n.value.toFixed(1) : n.value}
                  </p>
                  <p className="text-xs text-text-secondary">{n.unit}</p>
                </Card>
              );
            })}
          </div>
        </div>
      )}

      <h2 className="text-2xl font-bold text-white mb-4">Ingredient Breakdown</h2>
      <div className="flex flex-col gap-3 mb-10">
        {data.ingredients.map((ing, idx) => (
          <Card key={idx} className="p-4 flex flex-col md:flex-row gap-3 items-start md:items-center">
            <div className="flex items-center gap-3 min-w-[180px]">
              {getRiskIcon(ing.risk_level)}
              <span className="font-semibold text-white">{ing.name}</span>
            </div>
            <div className="flex-1">
              <p className="text-text-secondary text-sm">{ing.explanation}</p>
              {ing.safety_concern && (
                <p className="text-xs text-accent-warning mt-1 flex items-center gap-1">
                  <Shield className="w-3 h-3" />{ing.safety_concern}
                </p>
              )}
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge level={ing.risk_level as any}>{ing.risk_level}</Badge>
              {!ing.is_gras && <Chip className="text-xs bg-accent-danger/20 text-accent-danger border-accent-danger/30">Not GRAS</Chip>}
              {ing.flags.map(flag => (
                <Chip key={flag} className="text-xs bg-base-800 border-none">{flag.replace(/_/g, ' ')}</Chip>
              ))}
            </div>
          </Card>
        ))}
      </div>

      {data.alternatives.length > 0 && (
        <>
          <h2 className="text-2xl font-bold text-white mb-4">Healthier Alternatives</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {data.alternatives.map((alt, idx) => (
              <Card key={idx} hoverable className="border-accent/20 bg-accent/5">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle className="w-5 h-5 text-accent" />
                  <h3 className="font-semibold text-white">{alt.product_name ?? 'Alternative'}</h3>
                </div>
                {alt.brand && <p className="text-sm text-text-secondary mb-2">by {alt.brand}</p>}
                <p className="text-white text-sm bg-base-900/50 p-3 rounded-lg border border-base-700/50">{alt.reason}</p>
              </Card>
            ))}
          </div>
        </>
      )}
    </>
  );
};

const MedicineResults = ({ data }: { data: MedicineScanResult }) => (
  <div className="flex flex-col gap-6">
    <Card className="bg-primary/5 border-primary/20">
      <h3 className="text-lg font-bold text-primary mb-2 flex items-center gap-2"><Info className="w-5 h-5"/> AI Summary</h3>
      <p className="text-white text-sm">{data.ai_summary}</p>
    </Card>
    
    <div className="grid md:grid-cols-2 gap-6">
      <Card>
        <h3 className="text-sm font-medium text-text-secondary mb-3 uppercase tracking-wider">Active Ingredients</h3>
        <ul className="list-disc list-inside text-white text-sm">
          {data.active_ingredients.length > 0 ? data.active_ingredients.map((ing, i) => <li key={i}>{ing}</li>) : <li>None listed</li>}
        </ul>
      </Card>
      <Card>
        <h3 className="text-sm font-medium text-text-secondary mb-3 uppercase tracking-wider">Important Info</h3>
        <p className="text-white text-sm mb-2"><span className="text-text-secondary">Type:</span> {data.medicine_type || 'Unknown'}</p>
        <p className="text-white text-sm mb-2"><span className="text-text-secondary">Use:</span> {data.intended_use || 'Unknown'}</p>
        <p className="text-white text-sm"><span className="text-text-secondary">Classification:</span> {data.is_prescription ? 'Prescription (Rx)' : 'Over-the-Counter (OTC)'}</p>
      </Card>
    </div>

    {(data.warnings.length > 0 || data.safety_notes) && (
      <Card className="border-accent-warning/30 bg-accent-warning/5">
        <h3 className="text-sm font-medium text-accent-warning mb-3 uppercase tracking-wider flex items-center gap-2"><AlertTriangle className="w-4 h-4"/> Warnings & Safety</h3>
        {data.safety_notes && <p className="text-white text-sm mb-3">{data.safety_notes}</p>}
        <ul className="list-disc list-inside text-white text-sm">
          {data.warnings.map((w, i) => <li key={i}>{w}</li>)}
        </ul>
      </Card>
    )}

    {data.storage_instructions && (
      <Card>
        <h3 className="text-sm font-medium text-text-secondary mb-2 uppercase tracking-wider">Storage Instructions</h3>
        <p className="text-white text-sm">{data.storage_instructions}</p>
      </Card>
    )}
    
    <p className="text-text-secondary text-xs text-center mt-4">This information is for educational purposes only and is not medical advice.</p>
  </div>
);

const CosmeticResults = ({ data }: { data: CosmeticScanResult }) => (
  <div className="flex flex-col gap-6">
    <Card className="bg-primary/5 border-primary/20">
      <h3 className="text-lg font-bold text-primary mb-2">AI Summary</h3>
      <p className="text-white text-sm">{data.ai_summary}</p>
      <div className="flex gap-2 mt-4">
        <Chip>Type: {data.product_type || 'Unknown'}</Chip>
        <Chip>{data.has_artificial_fragrance ? 'Contains Artificial Fragrance' : 'No Artificial Fragrance'}</Chip>
        {data.skin_suitability && <Chip>For: {data.skin_suitability}</Chip>}
      </div>
    </Card>

    <h2 className="text-2xl font-bold text-white mt-4">Ingredient Overview</h2>
    <div className="flex flex-col gap-3">
      {data.key_ingredients.map((ing, idx) => (
        <Card key={idx} className="p-4 flex flex-col md:flex-row gap-3 items-start md:items-center">
          <div className="flex items-center gap-3 min-w-[180px]">
            {ing.is_safe ? <CheckCircle className="w-5 h-5 text-accent" /> : <AlertTriangle className="w-5 h-5 text-accent-warning" />}
            <span className="font-semibold text-white">{ing.name}</span>
          </div>
          <p className="text-text-secondary text-sm flex-1">{ing.explanation}</p>
        </Card>
      ))}
    </div>

    <div className="grid md:grid-cols-2 gap-6 mt-4">
      <Card>
        <h3 className="text-sm font-medium text-text-secondary mb-3 uppercase tracking-wider">Potential Allergens</h3>
        <ul className="list-disc list-inside text-white text-sm">
          {data.allergens.length > 0 ? data.allergens.map((a, i) => <li key={i}>{a}</li>) : <li>None detected</li>}
        </ul>
      </Card>
      <Card>
        <h3 className="text-sm font-medium text-text-secondary mb-3 uppercase tracking-wider">Preservatives</h3>
        <ul className="list-disc list-inside text-white text-sm">
          {data.preservatives.length > 0 ? data.preservatives.map((p, i) => <li key={i}>{p}</li>) : <li>None detected</li>}
        </ul>
      </Card>
    </div>

    {data.usage_precautions.length > 0 && (
      <Card className="border-accent-warning/30 bg-accent-warning/5">
        <h3 className="text-sm font-medium text-accent-warning mb-3 uppercase tracking-wider">Usage Precautions</h3>
        <ul className="list-disc list-inside text-white text-sm">
          {data.usage_precautions.map((w, i) => <li key={i}>{w}</li>)}
        </ul>
      </Card>
    )}
  </div>
);

const FertilizerResults = ({ data }: { data: FertilizerScanResult }) => {
  const getRiskLabel = (score: number) => {
    if (score >= 70) return { text: 'Low Handling Risk', color: 'text-accent' };
    if (score >= 40) return { text: 'Moderate Handling Risk', color: 'text-accent-warning' };
    return { text: 'High Handling Risk', color: 'text-accent-danger' };
  };
  const risk = getRiskLabel(data.chemical_safety_score);

  return (
  <div className="flex flex-col gap-6">
    <div className="grid md:grid-cols-3 gap-6">
      <Card className="flex flex-col items-center justify-center text-center bg-base-800">
        <h3 className="text-sm font-medium text-text-secondary mb-4 uppercase tracking-wider">Chemical Safety</h3>
        <Gauge value={data.chemical_safety_score} label="/ 100" />
        <p className={`mt-3 font-bold text-sm ${risk.color}`}>{risk.text}</p>
      </Card>
      <Card className="md:col-span-2">
        <h3 className="text-sm font-medium text-text-secondary mb-3 uppercase tracking-wider">Overview</h3>
        <p className="text-white text-sm mb-3">{data.ai_summary}</p>
        <div className="flex gap-2">
          {data.product_type && <Chip>Type: {data.product_type}</Chip>}
          {data.npk_composition && <Chip className="bg-primary/20 text-primary border-primary/30">NPK: {data.npk_composition}</Chip>}
        </div>
      </Card>
    </div>

    <div className="mb-2">
      <h2 className="text-xl font-bold text-white mb-4">Chemical Safety Score Breakdown</h2>
      <Card>
        <div className="flex flex-col gap-2">
          <div className="flex justify-between text-xs text-text-secondary uppercase tracking-wider pb-2 border-b border-base-700">
            <span>Factor</span>
            <span>Points</span>
          </div>
          <div className="flex justify-between text-sm py-1">
            <span className="text-text-secondary">Base Safety Score</span>
            <span className="text-white font-mono">100</span>
          </div>
          <div className="flex items-center justify-between py-1 border-b border-base-800/50">
            <div className="flex items-center gap-2">
              <TrendingDown className="w-4 h-4 text-accent-danger flex-shrink-0" />
              <span className="text-sm text-white">Hazard Penalties</span>
            </div>
            <span className="font-mono font-bold text-sm text-accent-danger">
              -{100 - data.chemical_safety_score}
            </span>
          </div>
          <div className="flex justify-between text-sm pt-2 border-t border-base-700">
            <span className="font-bold text-white">Final Safety Score</span>
            <span className="font-bold font-mono text-white">{data.chemical_safety_score}</span>
          </div>
        </div>
      </Card>
    </div>

    <div className="grid md:grid-cols-2 gap-6">
      <Card>
        <h3 className="text-sm font-medium text-text-secondary mb-3 uppercase tracking-wider">Chemical Components</h3>
        <ul className="list-disc list-inside text-white text-sm">
          {data.chemical_components.length > 0 ? data.chemical_components.map((c, i) => <li key={i}>{c}</li>) : <li>None listed</li>}
        </ul>
      </Card>
      <Card>
        <h3 className="text-sm font-medium text-text-secondary mb-3 uppercase tracking-wider">Intended Use</h3>
        <p className="text-white text-sm">{data.intended_agricultural_use || 'Not specified'}</p>
      </Card>
    </div>

    <Card className="border-accent-danger/30 bg-accent-danger/5">
      <h3 className="text-sm font-medium text-accent-danger mb-3 uppercase tracking-wider flex items-center gap-2"><AlertOctagon className="w-4 h-4"/> Hazard Warnings</h3>
      <ul className="list-disc list-inside text-white text-sm mb-4">
        {data.hazard_warnings.length > 0 ? data.hazard_warnings.map((w, i) => <li key={i}>{w}</li>) : <li>No explicit hazard warnings were detected on the visible packaging.</li>}
      </ul>
      
      <h3 className="text-sm font-medium text-accent-warning mb-2 uppercase tracking-wider">PPE Recommendations</h3>
      <div className="flex gap-2 flex-wrap">
        {data.ppe_recommendations.length > 0 ? data.ppe_recommendations.map((ppe, i) => <Chip key={i}>{ppe}</Chip>) : <span className="text-sm text-text-secondary">None specified</span>}
      </div>
    </Card>

    <div className="grid md:grid-cols-2 gap-6">
      <Card>
        <h3 className="text-sm font-medium text-text-secondary mb-3 uppercase tracking-wider">Storage</h3>
        <p className="text-white text-sm">{data.storage_instructions || 'Storage instructions were not clearly visible on the uploaded packaging.'}</p>
      </Card>
      <Card>
        <h3 className="text-sm font-medium text-text-secondary mb-3 uppercase tracking-wider">Environmental</h3>
        <ul className="list-disc list-inside text-white text-sm">
          {data.environmental_precautions.length > 0 ? data.environmental_precautions.map((w, i) => <li key={i}>{w}</li>) : <li>Not specified</li>}
        </ul>
      </Card>
    </div>
    
    <p className="text-accent-danger font-bold text-sm text-center mt-4 uppercase">Not intended for human or animal consumption.</p>
  </div>
)};

const PesticideResults = ({ data }: { data: PesticideScanResult }) => (
  <div className="flex flex-col gap-6">
    <div className="grid md:grid-cols-3 gap-6">
      <Card className="flex flex-col items-center justify-center text-center bg-base-800">
        <h3 className="text-sm font-medium text-text-secondary mb-4 uppercase tracking-wider">Chemical Safety</h3>
        <Gauge value={data.chemical_safety_score} label="/ 100" />
      </Card>
      <Card className="md:col-span-2">
        <h3 className="text-sm font-medium text-text-secondary mb-3 uppercase tracking-wider flex items-center gap-2"><AlertOctagon className="text-accent-danger w-5 h-5"/> Hazard: {data.hazard_classification || 'Unknown'}</h3>
        <p className="text-white text-sm mb-3">{data.ai_summary}</p>
        <div className="flex gap-2">
          {data.toxicity_level && <Chip className="bg-accent-danger/20 text-accent-danger border-accent-danger/30">Toxicity: {data.toxicity_level}</Chip>}
        </div>
      </Card>
    </div>

    <Card>
      <h3 className="text-sm font-medium text-text-secondary mb-3 uppercase tracking-wider">Active Ingredients</h3>
      <ul className="list-disc list-inside text-white text-sm">
        {data.active_ingredients.length > 0 ? data.active_ingredients.map((c, i) => <li key={i}>{c}</li>) : <li>None listed</li>}
      </ul>
    </Card>

    <Card className="border-accent-danger/30 bg-accent-danger/5">
      <h3 className="text-sm font-medium text-accent-danger mb-3 uppercase tracking-wider">Safe Handling & PPE</h3>
      <ul className="list-disc list-inside text-white text-sm mb-4">
        {data.safe_handling.length > 0 ? data.safe_handling.map((w, i) => <li key={i}>{w}</li>) : <li>Read label before use</li>}
      </ul>
      <div className="flex gap-2 flex-wrap">
        {data.ppe_recommendations.length > 0 ? data.ppe_recommendations.map((ppe, i) => <Chip key={i}>{ppe}</Chip>) : null}
      </div>
    </Card>

    <div className="grid md:grid-cols-2 gap-6">
      <Card>
        <h3 className="text-sm font-medium text-text-secondary mb-3 uppercase tracking-wider">Storage & Disposal</h3>
        <p className="text-white text-sm mb-2"><span className="text-text-secondary">Storage:</span> {data.storage_instructions || 'Not specified'}</p>
        <p className="text-white text-sm"><span className="text-text-secondary">Disposal:</span> {data.disposal_guidance || 'Not specified'}</p>
      </Card>
      <Card>
        <h3 className="text-sm font-medium text-text-secondary mb-3 uppercase tracking-wider">Environmental Risk</h3>
        <p className="text-white text-sm">{data.environmental_risk || 'Not specified'}</p>
      </Card>
    </div>
    
    <p className="text-accent-danger font-bold text-sm text-center mt-4 uppercase">This product contains agricultural chemicals and should be handled according to label instructions.</p>
  </div>
);

const HouseholdChemicalResults = ({ data }: { data: HouseholdChemicalScanResult }) => (
  <div className="flex flex-col gap-6">
    <div className="grid md:grid-cols-3 gap-6">
      <Card className="flex flex-col items-center justify-center text-center bg-base-800">
        <h3 className="text-sm font-medium text-text-secondary mb-4 uppercase tracking-wider">Chemical Safety</h3>
        <Gauge value={data.chemical_safety_score} label="/ 100" />
      </Card>
      <Card className="md:col-span-2">
        <h3 className="text-sm font-medium text-text-secondary mb-3 uppercase tracking-wider">Overview</h3>
        <p className="text-white text-sm mb-3">{data.ai_summary}</p>
        {data.product_type && <Chip>Type: {data.product_type}</Chip>}
      </Card>
    </div>

    <Card className="border-accent-warning/30 bg-accent-warning/5">
      <h3 className="text-sm font-medium text-accent-warning mb-3 uppercase tracking-wider flex items-center gap-2"><AlertTriangle className="w-4 h-4"/> Hazard Warnings</h3>
      <ul className="list-disc list-inside text-white text-sm mb-4">
        {data.hazard_warnings.length > 0 ? data.hazard_warnings.map((w, i) => <li key={i}>{w}</li>) : <li>No specific warnings detected</li>}
      </ul>
      {data.first_aid_information && (
        <>
          <h3 className="text-sm font-medium text-primary mb-2 uppercase tracking-wider">First Aid</h3>
          <p className="text-white text-sm">{data.first_aid_information}</p>
        </>
      )}
    </Card>

    <div className="grid md:grid-cols-2 gap-6">
      <Card>
        <h3 className="text-sm font-medium text-text-secondary mb-3 uppercase tracking-wider">Storage & Safety</h3>
        <p className="text-white text-sm mb-2"><span className="text-text-secondary">Storage:</span> {data.storage_instructions || 'Not specified'}</p>
        <p className="text-white text-sm"><span className="text-text-secondary">Child Safety:</span> {data.child_safety_advice || 'Keep out of reach of children.'}</p>
      </Card>
      <Card>
        <h3 className="text-sm font-medium text-text-secondary mb-3 uppercase tracking-wider">PPE Recommendations</h3>
        <div className="flex gap-2 flex-wrap">
          {data.ppe_recommendations.length > 0 ? data.ppe_recommendations.map((ppe, i) => <Chip key={i}>{ppe}</Chip>) : <span className="text-white text-sm">None specified</span>}
        </div>
      </Card>
    </div>
  </div>
);

const OtherResults = ({ data }: { data: OtherScanResult }) => (
  <div className="flex flex-col gap-6">
    <Card className="bg-primary/5 border-primary/20">
      <h3 className="text-lg font-bold text-primary mb-2">AI Summary</h3>
      <p className="text-white text-sm">{data.ai_summary}</p>
      {data.detected_type && <Chip className="mt-4">Detected Type: {data.detected_type}</Chip>}
    </Card>
    <Card>
      <h3 className="text-sm font-medium text-text-secondary mb-3 uppercase tracking-wider">Visible Information Extracted</h3>
      <p className="text-white text-sm font-mono whitespace-pre-wrap p-4 bg-base-900 rounded-lg">{data.extracted_text || 'No legible text found.'}</p>
    </Card>
  </div>
);


export const Results = () => {
  const { id } = useParams();
  const location = useLocation();
  const [data, setData] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (location.state?.result) {
      setData(location.state.result);
      return;
    }
    if (!id) return;
    scanService.getScan(id)
      .then(setData)
      .catch(err => {
        console.error(err);
        setError('Could not load scan results. Please try scanning again.');
      });
  }, [id, location.state]);

  if (error) return <div className="min-h-screen bg-base-900 flex items-center justify-center text-accent-danger font-medium px-6 text-center">{error}</div>;
  if (!data) return <div className="min-h-screen bg-base-900 flex items-center justify-center text-white">Loading Analysis...</div>;

  return (
    <div className="min-h-screen bg-base-900 pt-24 pb-12">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">

        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Link to="/scan" className="p-2 hover:bg-base-800 rounded-full text-text-secondary hover:text-white transition-colors">
            <ArrowLeft className="w-6 h-6" />
          </Link>
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-3xl font-bold text-white">{data.product_name ?? 'Unknown Product'}</h1>
              <Chip className="bg-primary/20 text-primary border-primary/30">{data.category || 'Food'}</Chip>
            </div>
            {('brand' in data && data.brand) && <p className="text-text-secondary text-lg">by {data.brand}</p>}
          </div>
        </div>

        {data.category === 'Food' || data.category === 'Beverage' || data.category === 'Fresh Produce' ? <FoodResults data={data as FoodScanResult} /> : null}
        {data.category === 'Medicine' ? <MedicineResults data={data as MedicineScanResult} /> : null}
        {data.category === 'Cosmetic' ? <CosmeticResults data={data as CosmeticScanResult} /> : null}
        {data.category === 'Fertilizer' ? <FertilizerResults data={data as FertilizerScanResult} /> : null}
        {data.category === 'Pesticide' ? <PesticideResults data={data as PesticideScanResult} /> : null}
        {data.category === 'Household Chemical' ? <HouseholdChemicalResults data={data as HouseholdChemicalScanResult} /> : null}
        {data.category === 'Other' ? <OtherResults data={data as OtherScanResult} /> : null}

      </div>
    </div>
  );
};
