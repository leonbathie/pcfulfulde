import { useCallback, useRef } from 'react';

interface LongPressOptions {
  threshold?: number; // ms, default 300ms
  onLongPress: (e: React.MouseEvent | React.TouchEvent) => void;
  onClick: (e: React.MouseEvent | React.TouchEvent) => void;
}

export function useLongPress({ threshold = 300, onLongPress, onClick }: LongPressOptions) {
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const isLongPressTriggered = useRef<boolean>(false);
  const startPos = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  const start = useCallback(
    (e: React.MouseEvent | React.TouchEvent) => {
      isLongPressTriggered.current = false;
      const clientX = 'touches' in e ? e.touches[0].clientX : (e as React.MouseEvent).clientX;
      const clientY = 'touches' in e ? e.touches[0].clientY : (e as React.MouseEvent).clientY;
      startPos.current = { x: clientX, y: clientY };

      timerRef.current = setTimeout(() => {
        isLongPressTriggered.current = true;
        onLongPress(e);
      }, threshold);
    },
    [onLongPress, threshold]
  );

  const clear = useCallback(
    (e: React.MouseEvent | React.TouchEvent, shouldTriggerClick = true) => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
      if (shouldTriggerClick && !isLongPressTriggered.current) {
        onClick(e);
      }
    },
    [onClick]
  );

  const move = useCallback((e: React.MouseEvent | React.TouchEvent) => {
    const clientX = 'touches' in e ? e.touches[0].clientX : (e as React.MouseEvent).clientX;
    const clientY = 'touches' in e ? e.touches[0].clientY : (e as React.MouseEvent).clientY;
    
    // If movement is > 10px, cancel long press
    if (
      Math.abs(clientX - startPos.current.x) > 10 ||
      Math.abs(clientY - startPos.current.y) > 10
    ) {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
    }
  }, []);

  return {
    onMouseDown: start,
    onMouseUp: (e: React.MouseEvent) => clear(e, true),
    onMouseLeave: (e: React.MouseEvent) => clear(e, false),
    onTouchStart: start,
    onTouchEnd: (e: React.TouchEvent) => clear(e, true),
    onTouchMove: move,
  };
}
