'use client';

import { useState } from 'react';
import { WIZARD_QUESTIONS, TOTAL_STEPS } from '@/lib/wizard-questions';
import { WizardAnswers } from '@/types/assessment';
import WizardStep from './WizardStep';

interface WizardShellProps {
  onComplete: (answers: WizardAnswers) => void;
}

export default function WizardShell({ onComplete }: WizardShellProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [answers, setAnswers] = useState<WizardAnswers>({});

  const question = WIZARD_QUESTIONS[currentStep - 1];
  const progress = Math.round((currentStep / TOTAL_STEPS) * 100);

  const handleAnswer = (value: string | string[] | boolean) => {
    setAnswers((prev) => ({ ...prev, [question.id]: value }));
  };

  const handleNext = () => {
    if (currentStep < TOTAL_STEPS) {
      setCurrentStep((s) => s + 1);
    } else {
      onComplete(answers);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) setCurrentStep((s) => s - 1);
  };

  const currentAnswer = answers[question.id];
  const canProceed = !question.required || currentAnswer !== undefined;

  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col">
      {/* Progress Bar */}
      <div className="w-full bg-slate-800 h-1.5">
        <div
          className="bg-blue-500 h-1.5 transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Step Counter */}
      <div className="max-w-2xl mx-auto w-full px-6 pt-8 pb-2 flex items-center justify-between text-sm text-slate-400">
        <span>Question {currentStep} of {TOTAL_STEPS}</span>
        <span>{progress}% complete</span>
      </div>

      {/* Question */}
      <div className="flex-1 flex items-center justify-center px-6 py-8">
        <div className="max-w-2xl w-full">
          <WizardStep
            question={question}
            value={currentAnswer}
            onChange={handleAnswer}
          />

          {/* Navigation */}
          <div className="flex justify-between mt-8">
            <button
              onClick={handleBack}
              disabled={currentStep === 1}
              className="px-6 py-3 rounded-xl border border-white/10 text-slate-300 hover:bg-white/5 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              ← Back
            </button>
            <button
              onClick={handleNext}
              disabled={!canProceed}
              className="px-8 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              {currentStep === TOTAL_STEPS ? 'Submit & Analyse →' : 'Next →'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
