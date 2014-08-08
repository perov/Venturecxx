{-# LANGUAGE RankNTypes #-}
{-# LANGUAGE ScopedTypeVariables #-}

module Utils (module Utils, module Unique) where

import Debug.Trace
import Data.List (find)
import qualified Data.Map as M
import qualified Data.Set as S
import Control.Lens
import Control.Monad.Coroutine -- from cabal install monad-coroutine
import Control.Monad.Morph
import Control.Monad.Identity
import Control.Monad.Trans.State.Lazy
import Text.PrettyPrint -- presumably from cabal install pretty

import Unique
import qualified InsertionOrderedSet as O

fromJust :: String -> Maybe a -> a
fromJust _ (Just a) = a
fromJust msg Nothing = error msg

-- A version of the ix lens that errors out if the value is not there
hardix :: (Ord k) => String -> k -> Simple Lens (M.Map k a) a
hardix msg k = lens find replace where
    find = fromJust msg . M.lookup k
    replace m a = case M.lookup k m of
                    (Just _) -> M.insert k a m
                    Nothing -> error msg

-- Suitable for counting with Data.Map.alter
maybeSucc :: Num a => Maybe a -> Maybe a
maybeSucc Nothing = Just 1
maybeSucc (Just x) = Just $ x+1

returnT :: (Monad n0, MFunctor t0) => t0 Identity b -> t0 n0 b
returnT = hoist (return . runIdentity)

modifyM :: Monad m => (s -> m s) -> StateT s m ()
modifyM act = get >>= (lift . act) >>= put

embucket :: (Num a, Ord b) => [(b, b)] -> [b] -> M.Map (b, b) a
embucket buckets values = foldl insert M.empty values where
    insert m v = case find (v `isInside`) buckets of
                   (Just b) -> M.alter maybeSucc b m
                   Nothing -> m
    isInside v (low,high) = low <= v && v <= high

buckets :: Int -> [Double] -> [(Double,Double)]
buckets ct values = zip lows (tail lows ++ [high]) where
    low = minimum values
    high = maximum values
    step = (high - low) / fromIntegral ct
    lows = [low,low+step..high]

histogram :: Int -> [Double] -> M.Map (Double,Double) Int
histogram ct values = embucket (buckets ct values) values where

discreteHistogram :: (Eq k, Ord k) => [k] -> M.Map k Int
discreteHistogram ks = foldl insert M.empty ks where
    insert m k = M.alter maybeSucc k m

printHistogram :: (Show k, Show a) => M.Map k a -> IO ()
printHistogram = mapM_ (putStrLn . show) . M.toList

-- TODO Check this with quickcheck (constraining ct to be positive)
-- See, e.g. http://stackoverflow.com/questions/3120796/haskell-testing-workflow
property_histogram_conserves_data :: Int -> [Double] -> Bool
property_histogram_conserves_data ct values = length values == (sum $ M.elems $ histogram ct values)

traceShowIt :: (Show a) => a -> a
traceShowIt it = traceShow it it

tracePrettyIt :: (Pretty a) => a -> a
tracePrettyIt it = traceShow (pp it) it

class Pretty a where
    pp :: a -> Doc

instance (Pretty a) => Pretty [a] where
    pp as = brackets $ sep $ map pp as

instance Pretty Doc where
    pp = id

instance (Pretty a) => Pretty (O.Set a) where
    pp as = brackets $ sep $ map pp $ O.toList as

instance (Pretty a) => Pretty (S.Set a) where
    pp as = brackets $ sep $ map pp $ S.toList as

pogoStickM :: forall m1 m2 s x. (Monad m1, Monad m2)
              => (m1 (m2 x) -> m2 (m1 x))
                 -> (m2 (m1 x) -> m1 (m2 x))
                 -> (s (Coroutine s m1 x) -> m2 (Coroutine s m1 x))
                 -> Coroutine s m1 x
                 -> m2 (m1 x)
pogoStickM swap swap' spring c = swap $ resume c >>= either continue stop where
    continue :: s (Coroutine s m1 x) -> m1 (m2 x)
    continue suspended = swap' act where
        act :: m2 (m1 x)
        act = do c' <- spring suspended
                 pogoStickM swap swap' spring c'
    stop :: x -> m1 (m2 x)
    stop = return . return

foldRunM :: forall s m t a x. (Monad m, MonadTrans t) =>
            (a -> s (Coroutine s (t m) x) -> m (a, (Coroutine s (t m) x))) ->
            Coroutine s (t m) x ->
            (t m) (a, x)
foldRunM spring c = undefined

-- Generalize foldRun to the case where the step function is itself a
-- coroutine, over the same underlying monad.
foldRunMC ::  forall s s2 m a x. (Monad m, Functor s2) =>
            (a -> s (Coroutine s m x) -> (Coroutine s2 m) ((Coroutine s m x), a)) ->
            a ->
            Coroutine s m x ->
            Coroutine s2 m (x, a)
foldRunMC = undefined

-- foldRunMC with a monad transformer.  In the case of recursive
-- regeneration, this achieves the effect of separating the weight log
-- and the TraceView changes between the inner and outer regen (the
-- outer log and changes travel through the value a in the spring
-- function, and the inner ones travel in the monad transformer t).
foldRunMC1 :: forall s s2 m t a x. (Monad m, MonadTrans t, Functor s2, Monad (t m)) =>
            (a -> s (Coroutine s (t m) x) -> (Coroutine s2 m) ((Coroutine s (t m) x), a)) ->
            a ->
            Coroutine s (t m) x ->
            Coroutine s2 (t m) (x, a)
foldRunMC1 spring start c = do
  step <- lift $ resume c
  case step of
    Right result -> return (result, start)
    Left susp -> do
      (c', start') <- mapMonad lift $ spring start susp
      foldRunMC1 spring start' c'

-- And now with *two* monad transformers
foldRunMC2 :: forall s s2 m t1 t2 a x. (Monad m, MonadTrans t1, MonadTrans t2, Functor s2, Monad (t1 (t2 m)), Monad (t2 m)) =>
            (a -> s (Coroutine s (t1 (t2 m)) x) -> (Coroutine s2 m) ((Coroutine s (t1 (t2 m)) x), a)) ->
            a ->
            Coroutine s (t1 (t2 m)) x ->
            Coroutine s2 (t1 (t2 m)) (x, a)
foldRunMC2 spring start c = do
  step <- lift $ resume c
  case step of
    Right result -> return (result, start)
    Left susp -> do
      (c', start') <- mapMonad (lift . lift) $ spring start susp
      foldRunMC2 spring start' c'
