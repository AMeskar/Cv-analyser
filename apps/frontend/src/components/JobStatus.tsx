import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';

interface JobStatusProps {
  jobId: string;
  cvId: string;
  onComplete?: () => void;
}

export default function JobStatus({ jobId, cvId, onComplete }: JobStatusProps) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['jobStatus', jobId],
    queryFn: () => apiClient.getJobStatus(jobId),
    refetchInterval: (data) => {
      // Poll every 2 seconds if job is not completed
      if (data?.status === 'completed' || data?.status === 'failed') {
        return false;
      }
      return 2000;
    },
  });

  useEffect(() => {
    if (data?.status === 'completed' && onComplete) {
      onComplete();
    }
  }, [data?.status, onComplete]);

  if (isLoading) {
    return <div className="job-status">Loading job status...</div>;
  }

  if (error) {
    return <div className="error">Failed to fetch job status</div>;
  }

  if (!data) {
    return null;
  }

  return (
    <div className="job-status">
      <h2>Analysis Status</h2>
      <div className="status-info">
        <p>
          <strong>Status:</strong> <span className={`status-${data.status}`}>{data.status}</span>
        </p>
        <p>
          <strong>Job ID:</strong> {jobId}
        </p>
        {data.error && (
          <div className="error">
            <strong>Error:</strong> {data.error}
          </div>
        )}
      </div>

      <div className="timeline">
        <h3>Timeline</h3>
        <ul>
          {data.timeline.map((event, idx) => (
            <li key={idx}>
              <span className="timestamp">{new Date(event.timestamp).toLocaleString()}</span>
              <span className="event">{event.event}</span>
              <span className="message">{event.message}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
