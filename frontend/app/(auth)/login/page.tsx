'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { loginUser } from '@/lib/authApi';
import { useAppStore } from '@/lib/store';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [hasAnimated, setHasAnimated] = useState(false);
  const router = useRouter();
  const { login } = useAppStore();

  useEffect(() => {
    // Check if animation has already played in this session
    const animated = sessionStorage.getItem('loginAnimated');
    if (animated) {
      setHasAnimated(true);
    } else {
      sessionStorage.setItem('loginAnimated', 'true');
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const data = await loginUser(email, password);
      login({ email }, data.access_token);
      router.push('/');
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred.');
      }
    }
  };

  return (
    <div className="space-y-8">
      {/* Animated Brand Section */}
      <div className="text-center space-y-4">
        <h1 className={`font-lobster text-8xl bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent ${hasAnimated ? '' : 'animate-write-in'}`}>
          Cue
        </h1>
        <p className={`font-lobster text-3xl text-gray-400 whitespace-nowrap ${hasAnimated ? '' : 'animate-write-subtitle'}`}>
          AI video editor for next generation
        </p>
        <div className="pt-12">
          <h2 className={`font-lobster text-4xl bg-gradient-to-r from-white via-gray-200 to-gray-400 bg-clip-text text-transparent ${hasAnimated ? '' : 'animate-write-welcome'}`}>
            Welcome Back
          </h2>
        </div>
      </div>

      {/* Login Form */}
      <div className={`mt-8 ${hasAnimated ? '' : 'animate-fade-in-form'}`}>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-5">
            <div>
              <label htmlFor="email-address" className="block text-sm font-medium text-gray-400 mb-2 tracking-wide">
                EMAIL
              </label>
              <input
                id="email-address"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="appearance-none block w-full px-4 py-3.5 border border-gray-800 bg-gray-900/50 text-white placeholder-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300 backdrop-blur-sm hover:border-gray-700"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-400 mb-2 tracking-wide">
                PASSWORD
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="appearance-none block w-full px-4 py-3.5 border border-gray-800 bg-gray-900/50 text-white placeholder-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300 backdrop-blur-sm hover:border-gray-700"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-3 animate-shake">
              <p className="text-red-400 text-sm text-center">{error}</p>
            </div>
          )}

          <button
            type="submit"
            className="w-full flex justify-center py-4 px-4 border border-transparent text-base font-bold rounded-xl text-white bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 hover:from-blue-700 hover:via-purple-700 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-black transition-all transform hover:scale-[1.02] active:scale-[0.98] shadow-lg hover:shadow-purple-500/50"
          >
            Sign In
          </button>
        </form>
        
        <div className="mt-8 text-center">
          <p className="text-gray-500 text-sm">
            Don't have an account?{' '}
            <Link href="/register" className="font-semibold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent hover:from-blue-300 hover:to-purple-300 transition-all">
              Sign up now
            </Link>
          </p>
        </div>
      </div>

      <style jsx>{`
        @keyframes write-in {
          0% {
            opacity: 0;
            clip-path: inset(0 100% 0 0);
          }
          100% {
            opacity: 1;
            clip-path: inset(0 0 0 0);
          }
        }

        @keyframes write-subtitle {
          0% {
            opacity: 0;
            clip-path: inset(0 100% 0 0);
          }
          100% {
            opacity: 1;
            clip-path: inset(0 0 0 0);
          }
        }

        @keyframes write-welcome {
          0% {
            opacity: 0;
            clip-path: inset(0 100% 0 0);
          }
          100% {
            opacity: 1;
            clip-path: inset(0 0 0 0);
          }
        }

        @keyframes fade-in-form {
          0% {
            opacity: 0;
            transform: translateY(20px);
          }
          100% {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-5px); }
          75% { transform: translateX(5px); }
        }

        .animate-write-in {
          animation: write-in 1.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        }

        .animate-write-subtitle {
          opacity: 0;
          animation: write-subtitle 2s cubic-bezier(0.4, 0, 0.2, 1) 1s forwards;
        }

        .animate-write-welcome {
          opacity: 0;
          animation: write-welcome 1.8s cubic-bezier(0.4, 0, 0.2, 1) 2.5s forwards;
        }

        .animate-fade-in-form {
          opacity: 0;
          animation: fade-in-form 1s ease-out 4s forwards;
        }

        .animate-shake {
          animation: shake 0.3s ease-in-out;
        }
      `}</style>
    </div>
  );
};

export default LoginPage;
