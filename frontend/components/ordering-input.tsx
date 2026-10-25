"use client";

import {
  DndContext,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  arrayMove,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { useEffect, useState } from "react";

export type OrderingItem = { id: string; label: string };

type Props = {
  items: OrderingItem[];
  disabled: boolean;
  onChange: (order: string[]) => void;
};

function Row({
  item,
  index,
  count,
  disabled,
  move,
}: {
  item: OrderingItem;
  index: number;
  count: number;
  disabled: boolean;
  move: (from: number, to: number) => void;
}) {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({
    id: item.id,
    disabled,
  });
  return (
    <li
      ref={setNodeRef}
      style={{ transform: CSS.Transform.toString(transform), transition }}
      className="flex items-center gap-2 rounded border border-surface-2 bg-surface-2 p-2 text-content-primary"
    >
      <button
        type="button"
        aria-label={`Déplacer ${item.label}`}
        disabled={disabled}
        className="cursor-grab px-1 text-content-muted"
        {...attributes}
        {...listeners}
      >
        ⠿
      </button>
      <span className="flex-1">{item.label}</span>
      <button
        type="button"
        aria-label={`Monter ${item.label}`}
        disabled={disabled || index === 0}
        onClick={() => move(index, index - 1)}
        className="px-1 disabled:opacity-30"
      >
        ↑
      </button>
      <button
        type="button"
        aria-label={`Descendre ${item.label}`}
        disabled={disabled || index === count - 1}
        onClick={() => move(index, index + 1)}
        className="px-1 disabled:opacity-30"
      >
        ↓
      </button>
    </li>
  );
}

/** Liste réordonnable (souris, clavier, boutons). Chargé à la demande. */
export default function OrderingInput({ items, disabled, onChange }: Props) {
  const [order, setOrder] = useState<OrderingItem[]>(items);
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  // L'ordre mélangé par le serveur est déjà une soumission valide.
  useEffect(() => {
    onChange(order.map((i) => i.id));
  }, [order, onChange]);

  const move = (from: number, to: number) => setOrder((o) => arrayMove(o, from, to));
  const onDragEnd = ({ active, over }: DragEndEvent) => {
    if (!over || active.id === over.id) return;
    setOrder((o) =>
      arrayMove(
        o,
        o.findIndex((i) => i.id === active.id),
        o.findIndex((i) => i.id === over.id),
      ),
    );
  };

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={onDragEnd}>
      <SortableContext items={order.map((i) => i.id)} strategy={verticalListSortingStrategy}>
        <ol aria-label="Éléments à ordonner" className="space-y-2">
          {order.map((item, index) => (
            <Row
              key={item.id}
              item={item}
              index={index}
              count={order.length}
              disabled={disabled}
              move={move}
            />
          ))}
        </ol>
      </SortableContext>
    </DndContext>
  );
}
