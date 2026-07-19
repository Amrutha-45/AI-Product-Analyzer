
import { Link } from 'react-router-dom';
import { ArrowRight, ShieldCheck, Zap, ScanLine } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';

export const Landing = () => {
  return (
    <div className="min-h-screen bg-base-900 pt-24 pb-12">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary mb-8 border border-primary/20">
          <Zap className="w-4 h-4" />
          <span className="text-sm font-medium">Powered by Gemini 2.5 Flash</span>
        </div>
        
        <h1 className="text-5xl md:text-7xl font-bold text-white tracking-tight mb-6">
          Know what you're <br className="hidden md:block" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">really eating.</span>
        </h1>
        
        <p className="text-xl text-text-secondary max-w-2xl mx-auto mb-10">
          Snap a photo of any product label. Our AI instantly breaks down the ingredients, spots hidden risks, and finds healthier alternatives.
        </p>
        
        <Link to="/scan">
          <Button size="lg" className="gap-2 group">
            Start Scanning
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Button>
        </Link>
      </div>

      {/* Feature Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="grid md:grid-cols-3 gap-8">
          <Card hoverable className="text-center group">
            <div className="mx-auto w-12 h-12 bg-primary/10 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <ScanLine className="w-6 h-6 text-primary" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-3">Instant Analysis</h3>
            <p className="text-text-secondary">
              Just upload front and back photos. We'll read the tiny text so you don't have to.
            </p>
          </Card>

          <Card hoverable className="text-center group">
            <div className="mx-auto w-12 h-12 bg-accent/10 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <ShieldCheck className="w-6 h-6 text-accent" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-3">Plain English</h3>
            <p className="text-text-secondary">
              No chemistry degree required. We explain what each ingredient is and why it matters.
            </p>
          </Card>

          <Card hoverable className="text-center group">
            <div className="mx-auto w-12 h-12 bg-accent-warning/10 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
              <Zap className="w-6 h-6 text-accent-warning" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-3">Better Choices</h3>
            <p className="text-text-secondary">
              If a product scores low, we'll suggest healthier alternatives from the same category.
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
};
