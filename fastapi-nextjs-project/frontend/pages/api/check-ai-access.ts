import type { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';

type ResponseData = {
  aiEnabled: boolean;
  redirect?: string;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<ResponseData>
) {
  const { redirect } = req.query;
  
  try {
    // Try to fetch AI status from the backend
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
    const response = await axios.get(`${apiUrl}/ai/status`);
    
    // Check if AI is enabled
    const aiEnabled = response.data?.enabled === true;
    
    if (aiEnabled) {
      // If AI is enabled, allow access to the AI route
      return res.status(200).json({ aiEnabled: true });
    } else {
      // If AI is disabled, redirect to home
      return res.redirect('/');
    }
  } catch (error) {
    // If there's an error (e.g., AI endpoints don't exist), redirect to home
    return res.redirect('/');
  }
}
