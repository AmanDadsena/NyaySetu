/**
 * Types for React's `<ViewTransition>`.
 *
 * The component is real and shipping — Next.js bundles a React build that
 * exports it (`next/dist/compiled/react`) and aliases `react` to that build
 * whenever `experimental.viewTransition` is set, which this project's
 * `next.config.ts` does. What is missing is only the *type*: the installed
 * `@types/react` (19.2.x stable) has no declaration for it, so without this
 * file `npx tsc --noEmit` fails on an import that works perfectly at runtime.
 *
 * Writing the props out rather than reaching for `any` is deliberate. A
 * mistyped prop here does not throw — it produces a component that renders
 * fine and simply never animates, which is close to impossible to notice.
 * Letting the compiler catch `entered` vs `enter` is the whole point.
 *
 * Delete this file once `@types/react` ships the declaration upstream.
 */

import type { ExoticComponent, ReactNode } from "react";

/**
 * Either one animation class for every navigation, or a map from transition
 * type (as passed to `<Link transitionTypes={[...]}>`) to a class. The
 * `default` key covers navigations carrying no type at all.
 */
type ViewTransitionClass = string | Record<string, string>;

export interface ViewTransitionProps {
  children?: ReactNode;
  /** Shared identity. Two elements with the same name morph into each other. */
  name?: string;
  enter?: ViewTransitionClass;
  exit?: ViewTransitionClass;
  share?: ViewTransitionClass;
  update?: ViewTransitionClass;
  /** Applied when no other prop matches. `"none"` opts out of unrelated transitions. */
  default?: ViewTransitionClass;
  onEnter?: (element: Element, types: string[]) => void;
  onExit?: (element: Element, types: string[]) => void;
  onShare?: (element: Element, types: string[]) => void;
  onUpdate?: (element: Element, types: string[]) => void;
}

declare module "react" {
  export const ViewTransition: ExoticComponent<ViewTransitionProps>;
}
