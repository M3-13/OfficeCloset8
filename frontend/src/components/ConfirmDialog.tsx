interface ConfirmDialogProps {
  open: boolean;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ConfirmDialog({ open, message, onConfirm, onCancel }: ConfirmDialogProps) {
  if (!open) return null;

  return (
    <div className="dialog-overlay" onClick={onCancel}>
      <div className="dialog" onClick={(e) => e.stopPropagation()}>
        <div className="dialog-spotlight" />
        <p className="dialog-message">{message}</p>
        <div className="dialog-actions">
          <button className="btn btn-secondary" onClick={onCancel}>
            Abbrechen
          </button>
          <button className="btn btn-danger" onClick={onConfirm}>
            Löschen
          </button>
        </div>
      </div>
    </div>
  );
}
