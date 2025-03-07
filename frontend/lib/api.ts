const API_URL = new URL(process.env.NEXT_PUBLIC_API_URL as string);

export async function apiRequest<T>(endpoint: string): Promise<T> {
    try {
        const response = await fetch(`${API_URL}${endpoint}`);
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        throw error instanceof Error 
          ? error 
          : new Error('An unknown error occurred while fetching data');
    }
}