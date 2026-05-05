import { ChevronsLeft, ChevronLeft, ChevronRight, ChevronsRight } from "lucide-react";
import { useEffect, useState } from "react";

type Props = {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
};

export function PaginationControls({ page, totalPages, onPageChange }: Props) {
  const [draftPage, setDraftPage] = useState(String(page));

  useEffect(() => {
    setDraftPage(String(page));
  }, [page]);

  function commitPage() {
    const nextPage = Number(draftPage);
    if (Number.isFinite(nextPage)) {
      onPageChange(Math.min(Math.max(Math.trunc(nextPage), 1), totalPages));
    }
  }

  return (
    <div className="pagination">
      <button
        className="icon-button"
        aria-label="First page"
        disabled={page <= 1}
        onClick={() => onPageChange(1)}
      >
        <ChevronsLeft size={18} />
      </button>
      <button
        className="icon-button"
        aria-label="Previous page"
        disabled={page <= 1}
        onClick={() => onPageChange(page - 1)}
      >
        <ChevronLeft size={18} />
      </button>
      <label className="page-jump">
        <span>Page</span>
        <input
          type="number"
          min={1}
          max={totalPages}
          value={draftPage}
          onChange={(event) => setDraftPage(event.target.value)}
          onBlur={commitPage}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              commitPage();
              event.currentTarget.blur();
            }
          }}
        />
        <span>of {totalPages}</span>
      </label>
      <button
        className="icon-button"
        aria-label="Next page"
        disabled={page >= totalPages}
        onClick={() => onPageChange(page + 1)}
      >
        <ChevronRight size={18} />
      </button>
      <button
        className="icon-button"
        aria-label="Last page"
        disabled={page >= totalPages}
        onClick={() => onPageChange(totalPages)}
      >
        <ChevronsRight size={18} />
      </button>
    </div>
  );
}
