import React from 'react';
import { createRoot } from 'react-dom/client';
import DynamicGamepad from './DynamicGamepad';

const container = document.getElementById('root');
const root = createRoot(container);
root.render(<DynamicGamepad />);