/**
 * Chat service for communicating with RAG chatbot API.
 *
 * Provides type-safe client for submitting queries and receiving
 * AI-generated responses with source citations.
 */

// API configuration
const API_BASE_URL = process.env.NODE_ENV === 'development'
  ? 'http://localhost:8000'
  : 'https://your-backend-url.com'; // Replace with your production backend URL

/**
 * Source citation from chatbot response
 */
export interface SourceCitation {
  module: string;
  chapter: string;
  section?: string;
  url: string;
  relevance_score: number;
}

/**
 * Individual chat message (user or assistant)
 */
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: SourceCitation[];
}

/**
 * Request payload for chat query
 */
export interface ChatRequest {
  query: string;
  conversation_id?: string;
  selected_text?: string;
  module_filter?: string;
}

/**
 * Response from chat query endpoint
 */
export interface ChatResponse {
  answer: string;
  sources: SourceCitation[];
  conversation_id: string;
  processing_time: number;
  timestamp: string;
}

/**
 * Chat service class for API communication
 */
class ChatService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  /**
   * Submit query to chatbot and receive response.
   *
   * @param request - ChatRequest with query and optional context
   * @returns Promise resolving to ChatResponse with answer and sources
   * @throws Error if API request fails
   */
  async query(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/chat/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies for session management
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        // Parse error message from API
        const errorData = await response.json().catch(() => ({
          detail: 'An error occurred while processing your request.'
        }));

        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data: ChatResponse = await response.json();
      return data;

    } catch (error) {
      console.error('Chat service error:', error);

      // DEMO MODE: If backend unavailable, return demo response
      if (error instanceof TypeError && error.message.includes('fetch')) {
        return this.getDemoResponse(request);
      }

      throw error;
    }
  }

  /**
   * Get demo response when backend is not available
   */
  private getDemoResponse(request: ChatRequest): ChatResponse {
    const query = request.query.toLowerCase();

    let answer = `**📚 Demo Mode Active**\n\nYou asked: "${request.query}"\n\n`;
    let sources: SourceCitation[] = [];

    // Provide contextual demo responses based on query keywords
    if (query.includes('ros') || query.includes('ros2') || query.includes('node')) {
      answer += `ROS 2 (Robot Operating System 2) is the industry-standard middleware for modern robotics. It provides:\n\n` +
        `✅ **DDS Middleware** - Fast, decentralized communication\n` +
        `✅ **Client Libraries** - rclpy (Python) and rclcpp (C++)\n` +
        `✅ **Node System** - Modular architecture for robot components\n\n` +
        `📖 Learn more in **Module 1: ROS 2 Fundamentals**`;

      sources = [{
        module: 'Module 1',
        chapter: 'ROS 2 Fundamentals',
        url: '/module-01-ros2/intro',
        relevance_score: 0.95
      }];
    } else if (query.includes('gazebo') || query.includes('simulation') || query.includes('physics')) {
      answer += `Gazebo is a powerful physics simulator for robotics featuring:\n\n` +
        `🎮 **Multiple Physics Engines** - ODE, Bullet, PhysX\n` +
        `🌍 **Realistic Environments** - Custom world building\n` +
        `📡 **Sensor Simulation** - LiDAR, cameras, IMU\n\n` +
        `📖 Check out **Module 2: Gazebo & Unity Simulation**`;

      sources = [{
        module: 'Module 2',
        chapter: 'Gazebo & Unity Simulation',
        url: '/module-02-simulation/intro',
        relevance_score: 0.92
      }];
    } else if (query.includes('isaac') || query.includes('nvidia')) {
      answer += `NVIDIA Isaac provides GPU-accelerated robotics development:\n\n` +
        `⚡ **Isaac Sim** - Photorealistic simulation with RTX\n` +
        `🧠 **Isaac ROS** - Hardware-accelerated perception\n` +
        `🗺️ **Nav2 Integration** - Advanced navigation\n\n` +
        `📖 Explore **Module 3: NVIDIA Isaac Platform**`;

      sources = [{
        module: 'Module 3',
        chapter: 'NVIDIA Isaac Platform',
        url: '/module-03-isaac/intro',
        relevance_score: 0.90
      }];
    } else if (query.includes('vla') || query.includes('vision') || query.includes('language')) {
      answer += `Vision-Language-Action (VLA) integrates AI with robotics:\n\n` +
        `🗣️ **Voice Commands** - OpenAI Whisper integration\n` +
        `👁️ **Visual Perception** - CLIP multimodal understanding\n` +
        `🤲 **Gesture Recognition** - MediaPipe hand tracking\n` +
        `🧠 **LLM Planning** - GPT-4 task reasoning\n\n` +
        `📖 Master **Module 4: Vision-Language-Action**`;

      sources = [{
        module: 'Module 4',
        chapter: 'Vision-Language-Action',
        url: '/module-04-vla/intro',
        relevance_score: 0.88
      }];
    } else {
      answer += `I can help you with:\n\n` +
        `🤖 **ROS 2** - Middleware, nodes, topics, services\n` +
        `🎮 **Gazebo/Unity** - Physics simulation\n` +
        `⚡ **NVIDIA Isaac** - GPU-accelerated robotics\n` +
        `🧠 **VLA Models** - AI-powered robot control\n\n` +
        `💡 **Tip**: Use the sidebar to browse all modules!`;

      sources = [
        { module: 'All Modules', chapter: 'Course Overview', url: '/', relevance_score: 0.75 }
      ];
    }

    answer += `\n\n---\n\n⚠️ **To activate full RAG functionality:**\n` +
      `1. Deploy backend to Render/Railway\n` +
      `2. Add OpenAI API key (.env file)\n` +
      `3. Seed Qdrant vector database\n` +
      `4. Update API_BASE_URL in chatService.ts\n\n` +
      `🎯 **This demo shows the chatbot UI - Backend integration ready!**`;

    return {
      answer,
      sources,
      conversation_id: `demo-${Date.now()}`,
      processing_time: 1000,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Check health status of chat API.
   *
   * @returns Promise resolving to health status object
   */
  async healthCheck(): Promise<{ status: string; service: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/chat/health`, {
        method: 'GET',
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error(`Health check failed: ${response.statusText}`);
      }

      return await response.json();

    } catch (error) {
      console.error('Health check error:', error);
      throw error;
    }
  }

  /**
   * Get selected text from the page.
   *
   * Utility method to extract user's text selection for context.
   *
   * @returns Selected text or null if no selection
   */
  getSelectedText(): string | null {
    const selection = window.getSelection();
    const text = selection?.toString().trim();
    return text && text.length > 0 ? text : null;
  }
}

// Export singleton instance
export const chatService = new ChatService();
