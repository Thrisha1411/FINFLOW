import React, { useEffect, useState } from 'react';
import { Upload, FileText, CheckCircle2, AlertCircle, ArrowRight, Loader2 } from 'lucide-react';
import api from '../api/client';
import type { Receipt } from '../types';

export const ReceiptScannerPage: React.FC = () => {
  const [receipts, setReceipts] = useState<Receipt[]>([]);
  const [uploading, setUploading] = useState(false);
  const [selectedReceipt, setSelectedReceipt] = useState<Receipt | null>(null);
  
  // Verification form
  const [merchantName, setMerchantName] = useState('');
  const [totalAmount, setTotalAmount] = useState('');
  const [confirming, setConfirming] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');

  const fetchReceipts = async () => {
    try {
      const res = await api.get('/receipts');
      setReceipts(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchReceipts();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    setSuccessMsg('');
    try {
      const res = await api.post('/receipts/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      fetchReceipts();
      handleSelectReceipt(res.data);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Upload failed.');
    } finally {
      setUploading(false);
    }
  };

  const handleSelectReceipt = (rec: Receipt) => {
    setSelectedReceipt(rec);
    setMerchantName(rec.merchant_name || 'Vendor');
    setTotalAmount(rec.total_amount ? rec.total_amount.toString() : '0.00');
  };

  const handleConfirm = async () => {
    if (!selectedReceipt) return;
    setConfirming(true);
    try {
      await api.post('/receipts/confirm', {
        receipt_id: selectedReceipt.id,
        merchant_name: merchantName,
        total_amount: parseFloat(totalAmount)
      });
      setSuccessMsg(`Successfully converted into settled financial transaction for ${merchantName}!`);
      fetchReceipts();
      setSelectedReceipt(null);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Confirmation failed.');
    } finally {
      setConfirming(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">AI Receipt & Invoice Scanner</h1>
        <p className="text-sm text-slate-400 mt-1">
          Automated OCR text extraction, SHA-256 duplicate detection, and structured Pydantic parsing.
        </p>
      </div>

      {successMsg && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-sm flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 shrink-0" />
          {successMsg}
        </div>
      )}

      {/* Drag & Drop Upload Banner */}
      <div className="bg-slate-900 border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-xl p-8 text-center transition">
        <Upload className="w-10 h-10 text-indigo-400 mx-auto mb-3" />
        <h2 className="text-base font-semibold text-white">Upload Invoices, Bills or Receipts</h2>
        <p className="text-xs text-slate-400 mt-1 mb-4">
          Supports PDF, JPG, PNG, and Plain Text (up to 10MB)
        </p>
        <label className="cursor-pointer inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-semibold shadow-md shadow-indigo-600/30 transition">
          {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
          <span>{uploading ? 'Extracting via OCR...' : 'Choose File to Scan'}</span>
          <input
            type="file"
            accept=".pdf,.png,.jpg,.jpeg,.txt"
            onChange={handleFileUpload}
            className="hidden"
            disabled={uploading}
          />
        </label>
      </div>

      {/* Split view: Uploaded Receipts List and Extracted Field Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Receipts List */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <h2 className="text-base font-semibold text-white">Uploaded Expense Documents</h2>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {receipts.map((r) => (
              <div
                key={r.id}
                onClick={() => handleSelectReceipt(r)}
                className={`p-3.5 rounded-lg border cursor-pointer transition flex items-center justify-between ${
                  selectedReceipt?.id === r.id
                    ? 'bg-indigo-600/10 border-indigo-500'
                    : 'bg-slate-950/60 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded bg-slate-800 text-indigo-400">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-white">{r.merchant_name || r.file_name}</h3>
                    <p className="text-xs text-slate-400">
                      {r.invoice_number ? `Inv: ${r.invoice_number} • ` : ''}
                      {new Date(r.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-sm font-bold text-white">
                    ${r.total_amount ? r.total_amount.toFixed(2) : '0.00'}
                  </span>
                  <div>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      {r.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Verification & Line Item Inspection */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <h2 className="text-base font-semibold text-white mb-1">Human-In-The-Loop Verification</h2>
          <p className="text-xs text-slate-400 mb-4">
            Verify AI OCR extractions before committing to persistent financial ledger.
          </p>

          {selectedReceipt ? (
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Extracted Merchant Name</label>
                <input
                  type="text"
                  value={merchantName}
                  onChange={(e) => setMerchantName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-750 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Extracted Total Amount ($)</label>
                <input
                  type="number"
                  step="0.01"
                  value={totalAmount}
                  onChange={(e) => setTotalAmount(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-750 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              {/* Line Items */}
              {selectedReceipt.line_items.length > 0 && (
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Parsed Line Items</label>
                  <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-1.5 text-xs">
                    {selectedReceipt.line_items.map((li, idx) => (
                      <div key={idx} className="flex justify-between text-slate-300">
                        <span>{li.description}</span>
                        <span className="font-mono text-white">${li.total_price.toFixed(2)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <button
                onClick={handleConfirm}
                disabled={confirming}
                className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm transition shadow-lg shadow-emerald-600/20"
              >
                {confirming ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
                <span>Confirm & Create Verified Transaction</span>
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-64 text-slate-500 text-xs">
              <AlertCircle className="w-8 h-8 mb-2 opacity-50" />
              <span>Select or upload a receipt to verify extracted fields.</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
