import { useCallback, useRef } from 'react';

interface WorkerMessage {
  type: string;
  data?: any;
  error?: string;
  result?: any;
}

export function useAttributionWorker() {
  const workerRef = useRef<Worker | null>(null);

  const analyzeWithWorker = useCallback(async (journeys: any[], alpha: number = 0.5): Promise<any> => {
    return new Promise((resolve, reject) => {
      // Create worker on demand
      if (!workerRef.current) {
        workerRef.current = new Worker('/workers/attribution.worker.js');
      }

      const worker = workerRef.current;

      const handleMessage = (event: MessageEvent) => {
        const message: WorkerMessage = event.data;
        
        switch (message.type) {
          case 'SUCCESS':
            worker.removeEventListener('message', handleMessage);
            worker.removeEventListener('error', handleError);
            resolve(message.result);
            break;
            
          case 'ERROR':
            worker.removeEventListener('message', handleMessage);
            worker.removeEventListener('error', handleError);
            reject(new Error(message.error));
            break;
        }
      };

      const handleError = (error: ErrorEvent) => {
        worker.removeEventListener('message', handleMessage);
        worker.removeEventListener('error', handleError);
        reject(new Error(error.message));
      };

      worker.addEventListener('message', handleMessage);
      worker.addEventListener('error', handleError);

      // Send analysis request
      worker.postMessage({
        type: 'ANALYZE',
        data: { journeys, alpha }
      });
    });
  }, []);

  const terminateWorker = useCallback(() => {
    if (workerRef.current) {
      workerRef.current.terminate();
      workerRef.current = null;
    }
  }, []);

  return {
    analyzeWithWorker,
    terminateWorker
  };
}