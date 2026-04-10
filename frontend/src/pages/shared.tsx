import { ReactNode } from 'react';
import { StatePanel } from '../components/StatePanel';

export function QueryBlock({ isLoading, isError, isEmpty, children }: { isLoading:boolean; isError:boolean; isEmpty:boolean; children:ReactNode }) {
  if (isLoading) return <StatePanel message="Loading..." />;
  if (isError) return <StatePanel message="Unable to load data." />;
  if (isEmpty) return <StatePanel message="No records found." />;
  return <>{children}</>;
}
