import React, { useRef, useState, useEffect, type ReactNode } from "react";

interface EllipsisCheckerProps {
  children: ReactNode;
  className?: string;
}

export const EllipsisChecker: React.FC<EllipsisCheckerProps> = ({
  children,
  className = "",
}) => {
  const textRef = useRef<HTMLDivElement>(null);
  const [isTruncated, setIsTruncated] = useState(false);

  const checkTruncation = () => {
    const element = textRef.current;
    if (element) {
      // Compare visible width against total scrollable content width
      setIsTruncated(element.scrollWidth > element.clientWidth);
    }
  };

  useEffect(() => {
    const element = textRef.current;
    if (!element) return;

    // Check on initial mount
    checkTruncation();

    // Re-check if window resizes
    window.addEventListener("resize", checkTruncation);

    // Re-check if content changes dynamically
    const observer = new ResizeObserver(() => checkTruncation());
    observer.observe(element);

    return () => {
      window.removeEventListener("resize", checkTruncation);
      observer.disconnect();
    };
  }, [children]);

  // Extract plain text for the title attribute if children is a string
  const tooltipText = typeof children === "string" ? children : undefined;

  return (
    <div
      ref={textRef}
      className={className}
      title={isTruncated ? tooltipText : undefined}
      style={{
        overflow: "hidden",
        textOverflow: "ellipsis",
        whiteSpace: "nowrap",
      }}
    >
      {children}
    </div>
  );
};
