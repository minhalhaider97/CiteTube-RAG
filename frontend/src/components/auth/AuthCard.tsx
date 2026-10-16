import { useState } from 'react';
import { supabase } from '../../lib/auth';
import { Video } from 'lucide-react';

interface AuthCardProps {
  initialError?: string | null;
}

export default function AuthCard({ initialError }: AuthCardProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(initialError || null);
  const [resendSent, setResendSent] = useState(false);

  const handleResendVerification = async () => {
    if (!email) {
      setError('Please enter your email above to resend the verification link.');
      return;
    }
    setLoading(true);
    const { error } = await supabase.auth.resend({
      type: 'signup',
      email,
    });
    setLoading(false);
    if (error) {
      setError(error.message);
    } else {
      setResendSent(true);
    }
  };

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (isSignUp) {
        const { error } = await supabase.auth.signUp({ email, password });
        if (error) throw error;
        alert('Check your email for the confirmation link!');
      } else {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#171717] px-4">
      <div className="w-full max-w-md rounded-xl bg-[#212121] p-8 shadow-2xl border border-[#303030]">
        <div className="flex flex-col items-center mb-6">
          <div className="rounded-full bg-white p-3 text-black mb-3">
            <Video className="h-6 w-6" />
          </div>
          <h2 className="text-2xl font-bold text-white">
            {isSignUp ? 'Create your account' : 'Welcome back'}
          </h2>
          <p className="text-sm text-neutral-400 mt-1">YouTube Video RAG Intelligence</p>
        </div>

        {error && (
          <div className="mb-4 rounded bg-red-950/50 p-3 border border-red-800/50 text-sm text-red-200">
            <p>{error}</p>
            {error.toLowerCase().includes('expired') || error.toLowerCase().includes('confirmation') ? (
              <button
                type="button"
                onClick={handleResendVerification}
                disabled={loading}
                className="mt-2 text-xs text-white underline hover:text-gray-300 disabled:opacity-50"
              >
                {resendSent ? 'Verification link sent!' : 'Resend verification email'}
              </button>
            ) : null}
          </div>
        )}

        <form onSubmit={handleAuth} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-neutral-300 mb-1">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-md bg-[#171717] border border-[#383838] px-3 py-2 text-sm text-white focus:outline-none focus:border-white"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-neutral-300 mb-1">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-md bg-[#171717] border border-[#383838] px-3 py-2 text-sm text-white focus:outline-none focus:border-white"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-white py-2 text-sm font-semibold text-black transition hover:bg-neutral-200 disabled:opacity-50"
          >
            {loading ? 'Processing...' : isSignUp ? 'Sign Up' : 'Log In'}
          </button>
        </form>

        <div className="mt-6 text-center text-xs text-neutral-400">
          {isSignUp ? 'Already have an account? ' : "Don't have an account? "}
          <button
            type="button"
            onClick={() => {
              setIsSignUp(!isSignUp);
              setError(null);
            }}
            className="font-semibold text-white hover:underline"
          >
            {isSignUp ? 'Log in' : 'Sign up'}
          </button>
        </div>
      </div>
    </div>
  );
}