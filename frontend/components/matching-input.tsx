"use client";

import {
  DndContext,
  KeyboardSensor,
  PointerSensor,
  useDraggable,
  useDroppable,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import { useEffect, useState } from "react";

export type MatchItem = { id: string; label: string };

type Props = {
  left: MatchItem[];
  right: MatchItem[];
  disabled: boolean;
  /** Reçoit les paires {left_id, right_id} ; vide tant que rien n'est associé. */
  onChange: (pairs: { left_id: string; right_id: string }[]) => void;
};

function Chip({ item, disabled }: { item: MatchItem; disabled: boolean }) {
  const { attributes, listeners, setNodeRef, transform } = useDraggable({
    id: item.id,
    disabled,
  });
  return (
    <button
      type="button"
      ref={setNodeRef}
      aria-label={`Glisser ${item.label}`}
      disabled={disabled}
      style={transform ? { transform: `translate(${transform.x}px, ${transform.y}px)` } : undefined}
      className="cursor-grab rounded border border-surface-2 bg-surface-2 px-2 py-1 text-content-primary"
      {...attributes}
      {...listeners}
    >
      {item.label}
    </button>
  );
}

function Slot({
  item,
  right,
  assigned,
  disabled,
  assign,
}: {
  item: MatchItem;
  right: MatchItem[];
  assigned: string | undefined;
  disabled: boolean;
  assign: (leftId: string, rightId: string | null) => void;
}) {
  const { setNodeRef, isOver } = useDroppable({ id: item.id, disabled });
  const current = right.find((r) => r.id === assigned);
  return (
    <li
      ref={setNodeRef}
      className={`flex items-center gap-3 rounded border p-2 text-content-primary ${
        isOver ? "border-accent" : "border-surface-2"
      }`}
    >
      <span className="flex-1">{item.label}</span>
      {current && <Chip item={current} disabled={disabled} />}
      <select
        aria-label={`Associer ${item.label} à`}
        disabled={disabled}
        value={assigned ?? ""}
        onChange={(e) => assign(item.id, e.target.value || null)}
        className="rounded border border-surface-2 bg-surface-2 p-1 text-content-primary"
      >
        <option value="">—</option>
        {right.map((r) => (
          <option key={r.id} value={r.id}>
            {r.label}
          </option>
        ))}
      </select>
    </li>
  );
}

/** Association gauche/droite : glisser-déposer (souris, clavier) ou liste de choix. */
export default function MatchingInput({ left, right, disabled, onChange }: Props) {
  // left_id -> right_id ; un élément de droite n'a qu'un seul partenaire.
  const [pairs, setPairs] = useState<Record<string, string>>({});
  const sensors = useSensors(useSensor(PointerSensor), useSensor(KeyboardSensor));

  useEffect(() => {
    onChange(Object.entries(pairs).map(([left_id, right_id]) => ({ left_id, right_id })));
  }, [pairs, onChange]);

  const assign = (leftId: string, rightId: string | null) =>
    setPairs((prev) => {
      const next = Object.fromEntries(Object.entries(prev).filter(([l, r]) => l !== leftId && r !== rightId));
      if (rightId) next[leftId] = rightId;
      return next;
    });

  const onDragEnd = ({ active, over }: DragEndEvent) => {
    if (over) assign(String(over.id), String(active.id));
  };

  const used = new Set(Object.values(pairs));
  return (
    <DndContext sensors={sensors} onDragEnd={onDragEnd}>
      <ul aria-label="Éléments à associer" className="space-y-2">
        {left.map((l) => (
          <Slot key={l.id} item={l} right={right} assigned={pairs[l.id]} disabled={disabled} assign={assign} />
        ))}
      </ul>
      <div aria-label="Réserve" className="mt-4 flex flex-wrap gap-2">
        {right
          .filter((r) => !used.has(r.id))
          .map((r) => (
            <Chip key={r.id} item={r} disabled={disabled} />
          ))}
      </div>
    </DndContext>
  );
}
