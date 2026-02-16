import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AnalysisResult } from '../models/api.interfaces';
import { ToastService } from '../services/toast.service';
import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';

@Component({
  selector: 'app-results',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './results.component.html',
  styleUrls: ['./results.component.css']
})
export class ResultsComponent implements OnInit {
  results = signal<AnalysisResult | null>(null);
  jobDescription = signal<string | null>(null);
  isLoading = signal<boolean>(true);

  // Helper signal to expose recruiter insights conveniently
  recruiterInsights = signal<any | null>(null);
  generatingReport = signal<boolean>(false);

  constructor(private router: Router, private toastService: ToastService) {}

  ngOnInit(): void {
    const navigation = history.state;
    
    if (navigation.results) {
      this.results.set(navigation.results);
      this.jobDescription.set(navigation.jobDescription || null);
      // map recruiter insights if available
      this.recruiterInsights.set(navigation.results.recruiter_insights || null);
      this.isLoading.set(false);
    } else {
      // If no results, redirect to upload page
      this.router.navigate(['/analyze']);
      return;
    }
  }

  getScoreColor(score: number): string {
    if (score >= 80) return '#10b981'; // green
    if (score >= 60) return '#f59e0b'; // amber
    return '#ef4444'; // red
  }

  getScoreGradient(score: number): string {
    const color = this.getScoreColor(score);
    return `conic-gradient(${color} ${score * 3.6}deg, #e5e7eb 0deg)`;
  }

  // Circular progress helper for ATS score visualization
  getCircleDash(score: number, radius = 52): { circumference: number; dashOffset: number } {
    const r = radius;
    const circumference = 2 * Math.PI * r;
    const dashOffset = circumference * (1 - (Math.max(0, Math.min(100, score)) / 100));
    return { circumference, dashOffset };
  }

  async downloadReport(): Promise<void> {
    if (this.generatingReport()) return;
    this.generatingReport.set(true);
    try {
      const results = this.results();
      if (!results) {
        this.toastService.error('No results', 'There are no results to generate a report from.');
        this.generatingReport.set(false);
        return;
      }

      const el = this.buildReportElement(results);
      document.body.appendChild(el);

      const canvas = await html2canvas(el as HTMLElement, { scale: 2, useCORS: true });
      const imgData = canvas.toDataURL('image/png');

      const pdf = new jsPDF('p', 'mm', 'a4');
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const imgProps: any = (pdf as any).getImageProperties(imgData);
      const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;

      pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);

      const candidateName = results.parsed_resume?.contact_info?.name || 'resume_report';
      pdf.save(`${candidateName.replace(/\s+/g, '_')}_report.pdf`);

      document.body.removeChild(el);
      this.toastService.success('Report ready', 'The PDF report has been downloaded.');
    } catch (err) {
      console.error(err);
      this.toastService.error('Report failed', 'Unable to generate the PDF report. Try again.');
    } finally {
      this.generatingReport.set(false);
    }
  }

  private buildReportElement(results: AnalysisResult): HTMLElement {
    const wrap = document.createElement('div');
    wrap.style.width = '800px';
    wrap.style.padding = '24px';
    wrap.style.boxSizing = 'border-box';
    wrap.style.background = '#ffffff';
    wrap.style.color = '#0f172a';
    wrap.style.fontFamily = 'Inter, Roboto, Arial, sans-serif';
    wrap.style.border = '1px solid #e6edf7';
    wrap.style.borderRadius = '8px';
    wrap.style.margin = '20px';

    const matchPercent = this.getMatchPercentage();

    const score = results.results.overall_score ?? 0;
    const scoreColor = score >= 80 ? '#10b981' : score >= 60 ? '#f59e0b' : '#ef4444';

    // simple categorization for technical skills (best-effort)
    const tech = results.results.skills_analysis?.technical_skills || [];
    const soft = results.results.skills_analysis?.soft_skills || [];
    const missing = results.results.skills_analysis?.missing_skills || [];

    const frontendKeywords = ['react','angular','vue','html','css','javascript','typescript','svelte'];
    const backendKeywords = ['node','express','django','flask','spring','java','ruby','rails','python','php','.net'];
    const cloudKeywords = ['aws','azure','gcp','google cloud','lambda','ecs','eks','cloud'];
    const toolsKeywords = ['docker','kubernetes','git','jenkins','circleci','github','gitlab','terraform'];

    const categorize = (items: string[]) => {
      const f: string[] = [];
      const b: string[] = [];
      const c: string[] = [];
      const t: string[] = [];
      const other: string[] = [];
      items.forEach(s => {
        const lower = s.toLowerCase();
        if (frontendKeywords.some(k => lower.includes(k))) f.push(s);
        else if (backendKeywords.some(k => lower.includes(k))) b.push(s);
        else if (cloudKeywords.some(k => lower.includes(k))) c.push(s);
        else if (toolsKeywords.some(k => lower.includes(k))) t.push(s);
        else other.push(s);
      });
      return { frontend: f, backend: b, cloud: c, tools: t, other };
    };

    const cat = categorize(tech);

    const strengths = this.recruiterInsights()?.resume_quality?.strengths || results.results.strengths || [];
    const weaknesses = this.recruiterInsights()?.resume_quality?.weaknesses || [];
    const recommendations = this.recruiterInsights()?.improvement_suggestions?.content_improvements || results.results.recommendations || [];

    const matchKeywords = results.results.keyword_match?.missing_keywords || [];

    const explanation = score >= 80 ? 'Strong — resume is likely ATS-friendly and well-optimized.' : score >= 60 ? 'Average — some optimizations recommended for better ATS compatibility.' : 'Needs Improvement — significant ATS and content changes recommended.';

    const html = `
      <div style="padding:12px 16px;border-bottom:1px solid #eef2ff;display:flex;justify-content:space-between;align-items:flex-start;">
        <div>
          <h1 style="margin:0;font-size:22px;color:#0f172a;letter-spacing:0.2px">Resume Analysis Report</h1>
          <div style="color:#475569;margin-top:6px;font-size:13px">Generated by Resume Analyzer</div>
        </div>
        <div style="text-align:right;color:#64748b;font-size:12px">${new Date().toLocaleString()}</div>
      </div>

      <section style="display:flex;gap:18px;padding:18px 0;border-bottom:1px solid #f1f5f9;align-items:center;">
        <div style="flex:0 0 220px;">
          <div style="font-size:12px;color:#64748b">Candidate Overview</div>
          <div style="font-weight:800;font-size:18px;color:#0f172a;margin-top:8px">${results.parsed_resume?.contact_info?.name || 'N/A'}</div>
          <div style="color:#475569;margin-top:6px;font-size:13px">${results.parsed_resume?.contact_info?.email || ''}${results.parsed_resume?.contact_info?.email && (results.parsed_resume?.contact_info?.phone) ? ' • ' : ''}${results.parsed_resume?.contact_info?.phone || ''}</div>
          <div style="color:#475569;margin-top:8px;font-size:13px">Experience: <strong style="color:#0f172a">${this.formatExperienceYears(results.results.experience_years)}</strong></div>
        </div>

        <div style="flex:1;display:flex;gap:18px;align-items:center;">
          <div style="width:120px;height:120px;border-radius:12px;background:linear-gradient(135deg,#60A5FA,#2563eb);display:flex;flex-direction:column;align-items:center;justify-content:center;color:white;box-shadow:0 8px 22px rgba(37,99,235,0.12)">
            <div style="font-size:28px;font-weight:900">${score}</div>
            <div style="font-size:12px;margin-top:6px;opacity:0.95">ATS Score</div>
          </div>
          <div style="flex:1;">
            <div style="font-weight:800;color:#0f172a;font-size:16px">${results.results.rating || ''}</div>
            <div style="margin-top:8px;color:#475569;font-size:13px">${results.results.summary || (this.recruiterInsights()?.summary || 'Summary not available')}</div>
            <div style="margin-top:10px;font-size:13px"><span style="display:inline-block;padding:6px 8px;border-radius:6px;background:${scoreColor};color:white;font-weight:700">${explanation.split(' — ')[0]}</span><span style="margin-left:10px;color:#64748b">${explanation.split(' — ')[1] || ''}</span></div>
          </div>
          <div style="flex:0 0 160px;text-align:right;">
            <div style="font-size:12px;color:#64748b">Match</div>
            <div style="font-weight:800;font-size:20px;color:#0f172a;margin-top:6px">${matchPercent !== null ? matchPercent + '%' : 'N/A'}</div>
            <div style="margin-top:6px;font-size:12px;color:#64748b">${matchPercent !== null ? 'Match vs job description' : ''}</div>
          </div>
        </div>
      </section>

      <section style="padding:18px 0;border-bottom:1px solid #f1f5f9;">
        <h2 style="margin:0 0 8px 0;color:#0f172a;font-size:16px">Resume Summary & Strengths</h2>
        <div style="color:#475569;font-size:13px;margin-bottom:8px">${(strengths.slice(0,3).join(' • ') || 'No high-level strengths available')}</div>
        <div style="display:flex;gap:12px;flex-wrap:wrap">
          ${(strengths || []).map((s: string) => `<span style="background:#ecfdf5;color:#065f46;padding:6px 10px;border-radius:6px;font-weight:700;font-size:13px;margin-bottom:6px">${s}</span>`).join('')}
        </div>
      </section>

      <section style="padding:18px 0;border-bottom:1px solid #f1f5f9;">
        <h2 style="margin:0 0 8px 0;color:#0f172a;font-size:16px">Skills Breakdown</h2>
        <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:10px">
          <div style="flex:1;min-width:180px">
            <div style="font-size:13px;color:#64748b;margin-bottom:6px">Frontend</div>
            <div>${(cat.frontend.length ? cat.frontend : ['—']).map(s => `<div style="padding:6px 8px;border-radius:6px;background:#eff6ff;color:#1d4ed8;display:inline-block;margin:4px 6px 4px 0">${s}</div>`).join('')}</div>
          </div>
          <div style="flex:1;min-width:180px">
            <div style="font-size:13px;color:#64748b;margin-bottom:6px">Backend</div>
            <div>${(cat.backend.length ? cat.backend : ['—']).map(s => `<div style="padding:6px 8px;border-radius:6px;background:#f0f9ff;color:#0369a1;display:inline-block;margin:4px 6px 4px 0">${s}</div>`).join('')}</div>
          </div>
          <div style="flex:1;min-width:180px">
            <div style="font-size:13px;color:#64748b;margin-bottom:6px">Cloud / Tools</div>
            <div>${(cat.cloud.concat(cat.tools, cat.other).length ? cat.cloud.concat(cat.tools, cat.other) : ['—']).map(s => `<div style="padding:6px 8px;border-radius:6px;background:#f8fafc;color:#0f172a;display:inline-block;margin:4px 6px 4px 0;border:1px solid #e6edf7">${s}</div>`).join('')}</div>
          </div>
        </div>
        <div style="margin-top:8px;font-size:13px;color:#64748b">Missing / Recommended Skills: ${(missing.length ? missing.join(', ') : 'None identified')}</div>
      </section>

      <section style="padding:18px 0;border-bottom:1px solid #f1f5f9;">
        <h2 style="margin:0 0 8px 0;color:#0f172a;font-size:16px">Job Match Details</h2>
        <div style="color:#475569;font-size:13px;margin-bottom:8px">Match Percentage: <strong style="color:#0f172a">${matchPercent !== null ? matchPercent + '%' : 'N/A'}</strong></div>
        <div style="color:#475569;font-size:13px;margin-bottom:8px">Missing Keywords: ${(matchKeywords.length ? matchKeywords.join(', ') : 'None')}</div>
        <div style="color:#475569;font-size:13px">Recommended Skills to Add: ${(missing.length ? missing.join(', ') : 'None')}</div>
      </section>

      <section style="padding:18px 0;border-bottom:1px solid #f1f5f9;">
        <h2 style="margin:0 0 8px 0;color:#0f172a;font-size:16px">Improvement Suggestions (Prioritized)</h2>
        <ol style="color:#475569;margin-left:18px">${(recommendations.length ? recommendations : ['No recommendations available']).map((r: any) => `<li style="margin-bottom:8px">${r}</li>`).join('')}</ol>
      </section>

      <section style="padding:18px 0;">
        <h2 style="margin:0 0 8px 0;color:#0f172a;font-size:16px">Final Recommendation & Next Steps</h2>
        <div style="color:#475569;font-size:13px;margin-bottom:8px">Overall: <strong style="color:#0f172a">${score >= 80 ? 'Strong candidate' : score >= 60 ? 'Potential fit with improvements' : 'Needs revision and optimization'}</strong></div>
        <ul style="color:#475569;margin-left:18px">${[
          'Optimize resume for target keywords and role.',
          'Emphasize top skills and quantify achievements.',
          'Address missing skills where feasible and include relevant projects.'
        ].map(s => `<li style="margin-bottom:6px">${s}</li>`).join('')}</ul>
      </section>

      <footer style="padding-top:12px;color:#94a3b8;font-size:12px;text-align:center;border-top:1px solid #f1f5f9;margin-top:12px">Resume Analyzer — recruiter-ready report</footer>
    `;

    wrap.innerHTML = html;
    // keep it off-screen while rendering
    wrap.style.position = 'absolute';
    wrap.style.left = '-9999px';
    wrap.style.top = '0';
    return wrap;
  }

  getScoreText(score: number): string {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    return 'Needs Work';
  }

  getMatchPercentage(): number | null {
    const results = this.results();
    if (!results?.results?.keyword_match) return null;
    
    const matched = results.results.keyword_match.matched_keywords?.length || 0;
    const total = matched + (results.results.keyword_match.missing_keywords?.length || 0);
    
    return total > 0 ? Math.round((matched / total) * 100) : null;
  }

  getCandidateEmail(): string | null {
    return this.recruiterInsights()?.candidate_details?.email || this.results()?.parsed_resume?.contact_info?.email || null;
  }

  getCandidatePhone(): string | null {
    const phone = this.recruiterInsights()?.candidate_details?.phone;
    if (phone && phone !== 'Not Found') return phone;
    const phoneFromParsed = this.results()?.parsed_resume?.contact_info?.phone;
    return phoneFromParsed || null;
  }

  hasUrgentWarnings(): boolean {
    const weaknesses = this.recruiterInsights()?.resume_quality?.weaknesses || [];
    return weaknesses.some((w: string) => w.toLowerCase().includes('urgent'));
  }

  getImprovementSuggestions(): string[] {
    return this.recruiterInsights()?.improvement_suggestions?.content_improvements || this.recruiterInsights()?.improvement_suggestions?.resume_formatting_improvements || [];
  }

  formatExperienceYears(years: number | string | undefined): string {
    if (!years) return 'Not specified';
    if (typeof years === 'string') return years;
    return years === 1 ? '1 year' : `${years} years`;
  }

  goBack(): void {
    this.router.navigate(['/analyze']);
  }

  startNewAnalysis(): void {
    this.router.navigate(['/analyze']);
  }

  hasJobDescription(): boolean {
    return !!this.jobDescription();
  }

  // Helper methods for checking data availability
  hasStrengths(): boolean {
    return !!(this.results()?.results?.strengths?.length);
  }

  hasSkillsAnalysis(): boolean {
    const skills = this.results()?.results?.skills_analysis;
    return !!(skills?.technical_skills?.length || skills?.soft_skills?.length || skills?.missing_skills?.length);
  }

  hasKeywordMatch(): boolean {
    const match = this.results()?.results?.keyword_match;
    return !!(match?.matched_keywords?.length || match?.missing_keywords?.length);
  }

  hasRecommendations(): boolean {
    return !!(this.results()?.results?.recommendations?.length);
  }

  // small helper to detect that results are present for showing content with transition
  hasResultsLoaded(): boolean {
    return !this.isLoading() && !!this.results();
  }
}