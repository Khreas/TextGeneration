from __future__ import print_function
import tensorflow as tf

import argparse
import os
import io
from six.moves import cPickle

from model import Model

from six import text_type

os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

def sample_args():
    parser = argparse.ArgumentParser(
                       formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--save_dir', type=str, default='save',
                        help='model directory to store checkpointed models')
    parser.add_argument('--nb_chars', type=int, default=500,
                        help='number of characters to sample')
    parser.add_argument('--prime', type=text_type, default=u' ',
                        help='prime text')
    parser.add_argument('--sample', type=int, default=1,
                        help='0 to use max at each timestep, 1 to sample at '
                             'each timestep, 2 to sample on spaces')

    parser.add_argument('--sample_dir', type=str, default='samples',
                        help='sample directory to store samples of generated text')
    parser.add_argument('--data_dir', type=str, default='data/tinyshakespeare',
                        help='data directory containing input.txt')
    parser.add_argument('--rnn_size', type=int, default=128,
                        help='size of RNN hidden state')
    parser.add_argument('--num_layers', type=int, default=2,
                        help='number of layers in the RNN')
    parser.add_argument('--model', type=str, default='lstm',
                        help='rnn, gru, lstm, or nas')
    parser.add_argument('--batch_size', type=int, default=50,
                        help='minibatch size')
    parser.add_argument('--seq_length', type=int, default=50,
                        help='RNN sequence length')
    parser.add_argument('--num_epochs', type=int, default=50,
                        help='number of epochs')
    parser.add_argument('--learning_rate', type=float, default=0.002,
                        help='learning rate')
    parser.add_argument('--nb_samples', type=int, default=6,
                        help='number of samples to be generated')

    args = parser.parse_args()
    sample(args)


def sample(args):

    sample_directory = os.path.join(args.sample_dir, args.model, str(args.num_layers), args.data_dir[5:])
    filename = args.model + '_' + str(args.num_layers) + '_' + str(args.rnn_size) + '_' + str(args.seq_length) + '_' + args.data_dir[5:]

    with open(os.path.join(args.save_dir, 'config.pkl'), 'rb') as f:
        saved_args = cPickle.load(f)
    with open(os.path.join(args.save_dir, 'chars_vocab.pkl'), 'rb') as f:
        chars, vocab = cPickle.load(f)
    model = Model(saved_args, training=False)
    with tf.Session() as sess:
        tf.global_variables_initializer().run()
        saver = tf.train.Saver(tf.global_variables())
        ckpt = tf.train.get_checkpoint_state(args.save_dir)
        if ckpt and ckpt.model_checkpoint_path:
            saver.restore(sess, ckpt.model_checkpoint_path)
            for i in range(args.nb_samples):
                if not os.path.isdir(sample_directory):
                    os.makedirs(sample_directory)
                with open(sample_directory + '/' + filename, 'a+') as out:
                    string = model.sample(sess, chars, vocab, args.nb_chars, args.prime,
                                       args.sample).encode('utf-8')
                    if i == 0:
                        out.write("[DEBUT DU TEXTE] \n\n")
                    out.write(string + '\n\n[FIN DU TEXTE] \n\n\n ---------------------------------------------------------------- \n\n\n')
                    if i != args.nb_samples - 1:
                        out.write("[DEBUT DU TEXTE] \n\n")
                    print("Successfully saved to " + sample_directory + '/' + filename)

if __name__ == '__main__':
    sample_args()
