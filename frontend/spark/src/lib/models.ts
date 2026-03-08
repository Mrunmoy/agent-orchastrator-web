export const providerModels: Record<string, string[]> = {
  claude: [
    'claude-opus-4-5',
    'claude-sonnet-4',
    'claude-3-5-sonnet-20241022',
    'claude-3-5-haiku-20241022'
  ],
  openai: [
    'gpt-4o',
    'gpt-4o-mini',
    'gpt-4-turbo',
    'gpt-3.5-turbo'
  ],
  gemini: [
    'gemini-2.0-flash-exp',
    'gemini-1.5-pro',
    'gemini-1.5-flash'
  ],
  ollama: [
    'llama-3.3',
    'llama-3.1',
    'mistral',
    'codellama',
    'deepseek-coder'
  ]
}

export const personalities = [
  'Software Developer',
  'QA Engineer',
  'DevOps Engineer',
  'Product Manager',
  'UX Designer',
  'Tech Lead',
  'Data Scientist',
  'Security Engineer'
]
