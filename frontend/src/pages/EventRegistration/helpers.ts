import type { Question } from 'app/services/bisTypes'
import type { FormAnswer } from './EventRegistrationForm'

/**
 * Merge two arrays of answers: current, which has the right structure, and previous, which may have some useful answers that we'll cherrypick
 * @param questions
 * @param current
 * @param previous
 * @returns
 */
export const mergeAnswers = (
  questions: Question[],
  current: FormAnswer[],
  previous?: FormAnswer[],
): FormAnswer[] => {
  // if there are no previous answers, return current
  if (!previous) return current

  // merge each answer correctly
  return current.map(({ question, answer }) => {
    const currentQuestion = questions.find(q => q.id === question)
    const previousAnswer = previous.find(a => a.question === question)

    let mergedAnswer: string | string[] = answer

    if (currentQuestion) {
      if (currentQuestion.data?.type === 'radio') {
        // see if previous answer is still in current question options
        if (
          typeof previousAnswer?.answer === 'string' &&
          currentQuestion.data.options &&
          currentQuestion.data.options.some(
            ({ option }) => option === previousAnswer.answer,
          )
        )
          mergedAnswer = previousAnswer.answer
        else if (typeof previousAnswer?.answer === 'object') {
          // find any one previously selected answer
          const oneOfSelectedAnswers = previousAnswer.answer.find(
            a =>
              currentQuestion.data?.options &&
              currentQuestion.data.options.some(({ option }) => option === a),
          )
          if (oneOfSelectedAnswers) mergedAnswer = oneOfSelectedAnswers
        }
      } else if (currentQuestion.data?.type === 'checkbox') {
        if (typeof previousAnswer?.answer === 'object') {
          mergedAnswer = previousAnswer.answer.filter(
            a =>
              currentQuestion.data?.options &&
              currentQuestion.data.options.some(({ option }) => option === a),
          )
        } else if (typeof previousAnswer?.answer === 'string') {
          mergedAnswer = [previousAnswer.answer].filter(
            a =>
              currentQuestion.data?.options &&
              currentQuestion.data.options.some(({ option }) => option === a),
          )
        }
      } else {
        if (typeof previousAnswer?.answer === 'object') {
          mergedAnswer = previousAnswer.answer.join(', ')
        } else if (typeof previousAnswer?.answer === 'string') {
          mergedAnswer = previousAnswer.answer
        }
      }
    }

    return {
      is_required: currentQuestion?.is_required ?? false,
      question,
      answer: mergedAnswer,
    }
  })
}
