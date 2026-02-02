import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';

interface ReportViewerProps {
  cvId: string;
}

export default function ReportViewer({ cvId }: ReportViewerProps) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['report', cvId],
    queryFn: () => apiClient.getReport(cvId),
    enabled: false, // Enable when job is completed
    retry: false,
  });

  if (isLoading) {
    return <div className="report-viewer">Loading report...</div>;
  }

  if (error) {
    return (
      <div className="report-viewer">
        <div className="error">Report not available yet. Please wait for analysis to complete.</div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="report-viewer">
      <h2>Analysis Report</h2>
      <div className="report-content">
        <div className="scores">
          <h3>Scores</h3>
          {data.scores?.map((score: any, idx: number) => (
            <div key={idx} className="score-item">
              <span className="category">{score.category}</span>
              <span className="score-value">{score.score}/100</span>
              <p className="description">{score.description}</p>
            </div>
          ))}
        </div>

        <div className="skills">
          <h3>Detected Skills</h3>
          <ul>
            {data.skills?.map((skill: string, idx: number) => (
              <li key={idx}>{skill}</li>
            ))}
          </ul>
        </div>

        <div className="gaps">
          <h3>Identified Gaps</h3>
          <ul>
            {data.gaps?.map((gap: string, idx: number) => (
              <li key={idx}>{gap}</li>
            ))}
          </ul>
        </div>

        <div className="improvement-plan">
          <h3>Improvement Plan</h3>
          <div className="plan-content">{data.improvement_plan}</div>
        </div>
      </div>
    </div>
  );
}
