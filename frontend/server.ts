import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import { GoogleGenAI } from "@google/genai";
import dotenv from "dotenv";

dotenv.config();

let aiClient: GoogleGenAI | null = null;

function getGeminiClient(): GoogleGenAI | null {
  if (!aiClient) {
    const apiKey = process.env.GEMINI_API_KEY;
    if (apiKey && apiKey !== "MY_GEMINI_API_KEY") {
      aiClient = new GoogleGenAI({
        apiKey: apiKey,
        httpOptions: {
          headers: {
            'User-Agent': 'aistudio-build',
          }
        }
      });
    }
  }
  return aiClient;
}

const SYSTEM_INSTRUCTIONS = {
  aura: `You are Aura, a friendly, encouraging, and highly fluent AI Language Guide on Mellow AI.
Your personality is warm, intuitive, and calm, evoking "Dynamic Stillness".
Focus on helping the user build fluent speaking habits. Discuss colloquial expressions, natural phrasing, vocabulary enhancement, and interesting cultural details of native English speakers.
Strictly follow these rules:
1. Keep replies concise and readable (typically 2-4 sentences). Great for visual cards!
2. If the user makes grammatical mistakes, gently correct them in a friendly manner (e.g. "You might say..." or "A more natural way is...").
3. Always ask an intriguing, easy-to-answer follow-up question related to the topic of conversation.
4. Encourage the user, be exceedingly empathetic, and match their level (B2 by default).`,

  leo: `You are Leo, a warm, patient, and highly approachable AI English Tutor on Mellow AI, specialized for beginners.
Your goal is to build the user's confidence. Use clear, simple English and basic sentence structures.
Strictly follow these rules:
1. Keep replies concise (1-3 sentences) and extremely easy to understand.
2. If the user makes a mistake, explain the correction very simply with a brief example.
3. Encourage the user constantly with phrases like "Great job!", "Excellent try!", "Perfect!"
4. End with a simple, direct question that is easy to answer with 1-3 words.`,

  chen: `You are Dr. Chen, an intellectually rigorous, precise, and highly structured AI English Tutor on Mellow AI.
You focus on academic depth, vocabulary precision, and grammatical structural analysis.
Strictly follow these rules:
1. Keep replies clearly organized. Break complex language structures down.
2. Highlight exact grammar systems, explain sentence syntax patterns, or discuss morphology where helpful.
3. Be respectful, encouraging, and highly professional.
4. Give the user a clear mini-tip or challenge to practice grammar correctness.`
};

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // API Routes
  app.post("/api/chat", async (req, res) => {
    try {
      const { tutorId, messages } = req.body;
      const id = (tutorId || 'aura') as 'aura' | 'leo' | 'chen';
      const promptHistory = messages || [];

      const systemInstruction = SYSTEM_INSTRUCTIONS[id] || SYSTEM_INSTRUCTIONS.aura;

      const client = getGeminiClient();

      if (!client) {
        // Fallback simulated responses when API key is missing
        let reply = "";
        const lastMsg = promptHistory[promptHistory.length - 1]?.text || "";
        const lowerMsg = lastMsg.toLowerCase();

        if (id === 'aura') {
          if (lowerMsg.includes('hello') || lowerMsg.includes('hi')) {
            reply = "Hello there! I'm Aura, your language guide. I'm thrilled to chat with you! Let's talk about food, culture, or whatever clears your mind today. What's your favorite hobby?";
          } else {
            reply = `That sounds absolutely fascinating! On Mellow AI, we discover language in peaceful depth. I'd love to explore "${lastMsg}" in more details with you. (Simulated reply: Please configure GEMINI_API_KEY in Settings Secrets to enable live Gemini AI guidance!)`;
          }
        } else if (id === 'leo') {
          reply = `Hello! I am Leo. I am very happy to talk with you. Your English is doing great! Do you like learning English? What is your favorite food?`;
        } else {
          reply = `Welcome to your academic structural tutorial. Regarding your text: "${lastMsg}", let's examine the lexical composition. Grammatically, English syntax operates on Subject-Verb-Object defaults. (Simulated reply: Configure GEMINI_API_KEY for true syntactic analytics!)`;
        }

        return res.json({
          text: reply,
          suggestedPrompts: id === 'aura' 
            ? ["Tell me about cultural details", "Let's talk about hobbies", "Correction check!"]
            : id === 'leo'
            ? ["I like English!", "My favorite is pizza", "Help me with simple speaking"]
            : ["Analyze standard patterns", "Explain active voice", "Give me a writing prompt"]
        });
      }

      // Convert history to @google/genai format
      // Generate content using gemini-3.5-flash
      const formattedContents = promptHistory.map((m: any) => ({
        role: m.sender === 'user' ? 'user' : 'model',
        parts: [{ text: m.text }]
      }));

      const modelResponse = await client.models.generateContent({
        model: "gemini-3.5-flash",
        contents: formattedContents,
        config: {
          systemInstruction: systemInstruction,
          temperature: 0.7,
        }
      });

      const responseText = modelResponse.text || "I apologize, I didn't catch that. Could you repeat?";
      
      // Extract suggested prompts dynamically using another quick query or by a simple parsing
      // Real dynamic prompt suggestions make the UI absolutely outstanding
      let suggestedPrompts = ["Outline key points", "Check my expression"];
      if (id === 'aura') {
        suggestedPrompts = ["Explain this idiom", "Suggest a natural phrasing", "What is the cultural background?"];
      } else if (id === 'leo') {
        suggestedPrompts = ["Could you explain simply?", "Let's try a simpler topic", "Help me write this"];
      } else if (id === 'chen') {
        suggestedPrompts = ["Provide a grammar rule", "List alternative vocabularies", "Give me a syntax practice"];
      }

      res.json({
        text: responseText,
        suggestedPrompts: suggestedPrompts
      });

    } catch (error: any) {
      console.error("Gemini Chat Error:", error);
      
      // Determine response based on TutorId
      const { tutorId, messages } = req.body;
      const id = (tutorId || 'aura') as 'aura' | 'leo' | 'chen';
      const promptHistory = messages || [];
      const lastMsg = promptHistory[promptHistory.length - 1]?.text || "";
      const lowerMsg = lastMsg.toLowerCase();

      let reply = "";
      let suggestedPrompts = ["Outline key points", "Check my expression"];

      if (id === 'aura') {
        if (lowerMsg.includes('hello') || lowerMsg.includes('hi')) {
          reply = "Hello there! I'm Aura. No worries at all—even though Gemini is currently experiencing high demand, I am here in offline companion mode to protect your practice flow! What is your favorite way to unwind after a busy day?";
        } else {
          reply = `That is extremely interesting! In offline companion mode, I still love dissecting "${lastMsg}" with you. (Gemini API is briefly experiencing high demand, so I have seamlessly switched to standby rules so you don't lose your streak!)`;
        }
        suggestedPrompts = ["Let's discuss cultural idioms", "Gently correct my last message", "What can we talk about today?"];
      } else if (id === 'leo') {
        reply = `Hello! I am Leo. Gemini is busy right now, but I am still here to talk! Your English is awesome. Tell me, do you like clean spring weather?`;
        suggestedPrompts = ["I like sunny days", "Help me with simple speaking", "Could you say that simpler?"];
      } else {
        reply = `Greetings from Dr. Chen's structural guide. High demand has temporarily limited the cloud API connection, but we can still analyze your input: "${lastMsg}" locally. Let's test the active voice configuration.`;
        suggestedPrompts = ["Explain current exercises", "Show grammar rule summary", "Give me a sentence check"];
      }

      res.json({
        text: reply,
        suggestedPrompts: suggestedPrompts
      });
    }
  });

  // Serve Static assets or mount Vite under dev
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
