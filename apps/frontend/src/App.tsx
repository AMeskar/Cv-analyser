import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import CVUpload from './components/CVUpload';
import JobStatus from './components/JobStatus';
import ReportViewer from './components/ReportViewer';
import './App.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  const [cvId, setCvId] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);

  return (
    <QueryClientProvider client={queryClient}>
      <div className="app">
        <header className="app-header">
          <h1>AI CV Analyzer</h1>
          <p>Upload your CV and get AI-powered analysis</p>
        </header>

        <main className="app-main">
          {!cvId && (
            <CVUpload
              onUploadSuccess={(cvId) => {
                setCvId(cvId);
              }}
            />
          )}

          {cvId && !jobId && (
            <div className="section">
              <h2>CV Uploaded Successfully</h2>
              <p>CV ID: {cvId}</p>
              <button
                onClick={async () => {
                  try {
                    const { apiClient } = await import('./api/client');
                    const result = await apiClient.analyzeCV(cvId);
                    setJobId(result.job_id);
                  } catch (error) {
                    console.error('Failed to start analysis:', error);
                    alert('Failed to start analysis. Please try again.');
                  }
                }}
              >
                Start Analysis
              </button>
            </div>
          )}

          {jobId && (
            <>
              <JobStatus
                jobId={jobId}
                cvId={cvId!}
                onComplete={() => {
                  // Analysis complete, show report
                }}
              />
              <ReportViewer cvId={cvId!} />
            </>
          )}
        </main>
      </div>
    </QueryClientProvider>
  );
}

export default App;
